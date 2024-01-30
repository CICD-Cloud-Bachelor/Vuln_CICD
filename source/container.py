import pulumi
import pulumi_azure as azure
import pulumi_docker as docker
import pulumi_azure_native as azure_native
from pulumi_azure_native import containerinstance, resources
from pulumi_azure_native import network, dbformysql

class CreateContainer:    
    def __init__(self, resource_group, name: str, image: str, memory: float, port: int, cpu: int):
        self.resource_group = resource_group
        self.name = name
        self.image = image
        self.port = port
        self.memory = memory
        self.cpu = cpu
        self.create_container()
        self.export_container()


    def create_container(self) -> None:
        pulumi.log.debug(f"Creating container: {self.name}")
        self.container_group = azure.containerservice.Group(self.name,
            resource_group_name=self.resource_group.name,
            os_type='Linux',
            containers=[{
                'name': self.name,
                'image': self.image,
                'memory': self.memory,
                'ports': [{
                    'port': self.port,
                    'protocol': 'TCP',
                }],
                'cpu': self.cpu,
            }],
            ip_address_type='public',
            dns_name_label=self.name,
            restart_policy='OnFailure',
            tags={
                'environment': 'production',
            }
        )
        pulumi.log.info(f"Container created: {self.name}")

    def export_container(self) -> None:
        pulumi.export('container_group_ip_address', self.container_group.ip_address)
        self.container_group.ip_address.apply(lambda ip: pulumi.log.info(f"Container IP address exported: {ip}"))



class DockerACR:
    IMAGE_TAG = "v1.0"
    DNS_LABEL = "pulumibachelorproject"
    def __init__(self, resource_group, registry_name) -> None:
        self.resource_group = resource_group
        self.registry_name = registry_name
        self.__create_registry()


    def __create_registry(self) -> None:
        pulumi.log.info(f"Creating registry: {self.registry_name}")
        self.registry = azure_native.containerregistry.Registry(
            self.registry_name,
            resource_group_name=self.resource_group.name,
            sku=azure_native.containerregistry.SkuArgs(
                name="Basic"
            ),
            location=self.resource_group.location,
            admin_user_enabled=True,
        )

        # Obtain registry credentials for Docker
        self.credentials = pulumi.Output.all(self.resource_group.name, self.registry.name).apply(
            lambda args: azure_native.containerregistry.list_registry_credentials(
                resource_group_name=args[0],
                registry_name=args[1]
            )
        )

    def build_and_push_docker_image(self, image_name: str) -> str:
        pulumi.log.info(f"Building and pushing docker image: {image_name}")
        
        image_context_path = f"source/docker_images/{image_name}"
        dockerfile_path = f"{image_context_path}/Dockerfile" 
        image_name_with_tag = pulumi.Output.all(self.registry.login_server, image_name, self.IMAGE_TAG).apply(lambda args: f"{args[0].lower()}/{args[1]}:{args[2]}")
        
        # Define a Docker image resource that builds and pushes the image
        image = docker.Image(
            "myimage",
            image_name=image_name_with_tag,
            build=docker.DockerBuildArgs(
                context=image_context_path,
                dockerfile=dockerfile_path,
                platform="linux/amd64",
            ),
            registry=docker.RegistryArgs(
                server=self.registry.login_server.apply(lambda server: server),
                username=self.credentials.apply(lambda creds: creds.username),
                password=self.credentials.apply(lambda creds: creds.passwords[0].value),
            ),
            skip_push=False,
        )

        pulumi.export("image_name", image.image_name.apply(lambda name: name))
        return image.image_name.apply(lambda name: name)

    def start_container(self, image_name: str, container_name: str, port: int, cpu: float, memory: float):
        pulumi.log.info(f"Starting container: {container_name}")
        
        container_group_name = container_name + "-group"
        
        # Create a container group with a single container
        container_group = containerinstance.ContainerGroup(
            container_group_name,
            resource_group_name=self.resource_group.name,
            os_type="Linux",  # or "Windows"
            containers=[
                containerinstance.ContainerArgs(
                    name=container_name,
                    image=image_name,
                    resources=containerinstance.ResourceRequirementsArgs(
                        requests=containerinstance.ResourceRequestsArgs(
                            cpu=cpu,
                            memory_in_gb=memory,
                        ),
                    ),
                    ports=[containerinstance.ContainerPortArgs(port=port)],
                ),
            ],
            image_registry_credentials=[
                containerinstance.ImageRegistryCredentialArgs(
                    server=self.registry.login_server.apply(lambda server: server),
                    username=self.credentials.apply(lambda creds: creds.username),
                    password=self.credentials.apply(lambda creds: creds.passwords[0].value),
                ),
            ],
            ip_address=containerinstance.IpAddressArgs(
                ports=[containerinstance.PortArgs(
                    protocol="TCP",
                    port=port,
                )],
                type="Public",
                dns_name_label=f"{container_name}{self.DNS_LABEL}", # optional
            ),
            restart_policy="OnFailure",
        )

        # Construct the FQDN
        fqdn = pulumi.Output.all(container_group.name, container_group.location).apply(
            lambda args: f"{container_name}{self.DNS_LABEL}.{args[1]}.azurecontainer.io"
        )

        # Export the FQDN
        pulumi.export('fqdn', fqdn)
        pulumi.export("container_group_id", container_group.id)
