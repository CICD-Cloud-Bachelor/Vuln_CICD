import pulumi
import pulumi_azure as azure
import pulumi_docker as docker
import pulumi_azure_native as azure_native
from pulumi_azure_native import containerinstance, resources
from pulumi_azure_native import network, dbformysql

class CreateContainer:
    """
    A class representing a container creation and export.

    Args:
        resource_group (str): The name of the resource group.
        name (str): The name of the container.
        image (str): The image to use for the container.
        memory (float): The memory limit for the container.
        port (int): The port to expose for the container.
        cpu (int): The CPU limit for the container.
    """

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
        """
        Creates a container using the specified parameters.
        """
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
        """
        Exports the container's IP address.
        """
        pulumi.export('container_group_ip_address', self.container_group.ip_address)
        self.container_group.ip_address.apply(lambda ip: pulumi.log.info(f"Container IP address exported: {ip}"))



class DockerACR:
    """
    DockerACR class represents a Docker Azure Container Registry.

    Args:
        resource_group (pulumi.ResourceGroup): The resource group where the registry will be created.
        registry_name (str): The name of the registry.

    Attributes:
        IMAGE_TAG (str): The tag for the Docker image.
        DNS_LABEL (str): The DNS label for the container group.

    Methods:
        __init__(self, resource_group, registry_name): Initializes a new instance of the DockerACR class.
        __create_registry(self): Creates the Azure Container Registry.
        build_and_push_docker_image(self, image_name): Builds and pushes a Docker image to the registry.
        start_container(self, image_name, container_name, ports, cpu, memory): Starts a container in a container group.

    """

    IMAGE_TAG = "v1.0"
    DNS_LABEL = "pulumibachelorproject"

    def __init__(self, resource_group, registry_name) -> None:
        """
        Initializes a new instance of the DockerACR class.

        Args:
            resource_group (pulumi.ResourceGroup): The resource group where the registry will be created.
            registry_name (str): The name of the registry.

        """
        self.resource_group = resource_group
        self.registry_name = registry_name
        self.__create_registry()

    def __create_registry(self) -> None:
        """
        Creates the Azure Container Registry.
        """
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
        """
        Builds and pushes a Docker image to the registry.

        Args:
            image_name (str): The name of the Docker image.

        Returns:
            str: The name of the pushed Docker image.

        """
        pulumi.log.info(f"Building and pushing docker image: {image_name}")
        
        image_context_path = f"source/docker_images/{image_name}"
        dockerfile_path = f"{image_context_path}/Dockerfile" 
        image_name_with_tag = pulumi.Output.all(self.registry.login_server, image_name, self.IMAGE_TAG).apply(lambda args: f"{args[0].lower()}/{args[1]}:{args[2]}")
        
        # Define a Docker image resource that builds and pushes the image
        image = docker.Image(
            image_name,
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

    def start_container(self, docker_acr_image_name: str, container_name: str, ports: list[int], cpu: float, memory: float) -> str:
        """
        Starts a container in a container group.

        Args:
            docker_acr_image_name (str): The name of the Docker image.
            container_name (str): The name of the container.
            ports (list[int]): The list of ports to expose.
            cpu (float): The CPU resource limit for the container.
            memory (float): The memory resource limit for the container.

        Returns:
            str: The fully qualified domain name (FQDN) of the container.

        """
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
                    image=docker_acr_image_name,
                    resources=containerinstance.ResourceRequirementsArgs(
                        requests=containerinstance.ResourceRequestsArgs(
                            cpu=cpu,
                            memory_in_gb=memory,
                        ),
                    ),
                    ports=[containerinstance.ContainerPortArgs(port=p) for p in ports],
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
                ports=[containerinstance.PortArgs(protocol="TCP", port=p) for p in ports],
                type="Public",
                dns_name_label=f"{container_name}{self.DNS_LABEL}", # optional
            ),
            restart_policy="OnFailure",
        )

        # Construct the FQDN
        fqdn = pulumi.Output.all(container_group.name, container_group.location).apply(
            lambda args: f"{container_name}{self.DNS_LABEL}.{args[1]}.azurecontainer.io"
        )

        return fqdn
