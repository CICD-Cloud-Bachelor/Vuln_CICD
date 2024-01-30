import pulumi
import pulumi_azure as azure
import pulumi_docker as docker
import pulumi_azure_native as azure_native

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



class ImportDockerImageToACR:
    REGISTRY_NAME = "myregistry" 
    IMAGE_TAG = "v1.0"
    def __init__(self, resource_group, image_name) -> None:
        self.resource_group = resource_group
        self.image_name = image_name
        self.image_context_path = f"source/docker_images/{self.image_name}"
        self.dockerfile_path = f"{self.image_context_path}/Dockerfile" 
        self.__create_registry()


    def __create_registry(self) -> None:
        pulumi.log.debug(f"Creating registry: {self.REGISTRY_NAME}")
        self.registry = azure_native.containerregistry.Registry(
            self.REGISTRY_NAME,
            resource_group_name=self.resource_group.name,
            sku=azure_native.containerregistry.SkuArgs(
                name="Basic"
            ),
            location=self.resource_group.location,
            admin_user_enabled=True,
        )

        self.image_name_with_tag = pulumi.Output.all(self.registry.login_server, self.image_name, self.IMAGE_TAG).apply(lambda args: f"{args[0].lower()}/{args[1]}:{args[2]}")


        # Obtain registry credentials for Docker
        self.credentials = pulumi.Output.all(self.resource_group.name, self.registry.name).apply(
            lambda args: azure_native.containerregistry.list_registry_credentials(
                resource_group_name=args[0],
                registry_name=args[1]
            )
        )

    def build_and_push_docker(self) -> str:
        # Define a Docker image resource that builds and pushes the image
        image = docker.Image(
            "myimage",
            image_name=self.image_name_with_tag,
            build=docker.DockerBuildArgs(
                context=self.image_context_path,
                dockerfile=self.dockerfile_path,
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
