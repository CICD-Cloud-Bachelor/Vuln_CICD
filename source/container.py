import pulumi
import pulumi_azure as azure
import pulumi_docker as docker
import pulumi_azure_native as azure_native
from pulumi_azure_native import containerinstance, resources
from pulumi_azure_native import network, dbformysql
import configparser, requests

config = configparser.ConfigParser()
config.read('config.ini')
DNS_LABEL = config["DOCKER"]["DNS_LABEL"]
index = 0

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

    def __init__(
            self, 
            resource_group: azure.core.ResourceGroup, 
            name: str, 
            image: str, 
            memory: float, 
            port: int, 
            cpu: int
        ) -> None:
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

    Methods:
        __init__(self, resource_group, registry_name): Initializes a new instance of the DockerACR class.
        __create_registry(self): Creates the Azure Container Registry.
        build_and_push_docker_image(self, image_name): Builds and pushes a Docker image to the registry.
        start_container(self, image_name, container_name, ports, cpu, memory): Starts a container in a container group.

    """

    IMAGE_TAG = "v1.0"

    def __init__(
            self, 
            resource_group: azure.core.ResourceGroup, 
            registry_name: str
        ) -> None:
        """
        Initializes a new instance of the Docker Azure Container Registry class.

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
            resource_name=self.registry_name,
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

    def get_public_ip(self) -> str:
        return requests.get('https://api64.ipify.org').text

    def build_and_push_docker_image(
            self, 
            image_name: str #image name needs to be same as in github repo
        ) -> str:
        pulumi.log.info(f"Building and pushing Docker image: {image_name}")
        self.task = azure_native.containerregistry.TaskRun(f"taskRun{image_name}",
            force_update_tag="test",
            location=self.resource_group.location,
            registry_name=self.registry.name,
            resource_group_name=self.resource_group.name,
            run_request=azure_native.containerregistry.DockerBuildRequestArgs(
                source_location=f"https://github.com/CICD-Cloud-Bachelor/Docker_Images.git#:{image_name}",
                docker_file_path="Dockerfile",
                image_names=[f"image/{image_name}:{self.IMAGE_TAG}"],
                is_push_enabled=True,
                no_cache=False,
                type="Docker",
                platform=azure_native.containerregistry.PlatformPropertiesArgs(
                    # architecture="amd64",
                    os="Linux",
                ),
            ),
            task_run_name=f"myRunbuild{image_name}"
        )   
        
        return self.registry.login_server.apply(lambda login_server: f"{login_server}/image/{image_name}:{self.IMAGE_TAG}")


    def start_container(
            self, 
            docker_acr_image_name: str, 
            container_name: str, 
            ports: list[int], 
            cpu: float, 
            memory: float
        ) -> str:
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

        global index
        # Create a network security group
        self.nsg = network.NetworkSecurityGroup(
            f'pulumi-nsg-{index}',
            resource_group_name=self.resource_group.name
        )

        # Define a security rule to allow traffic from a specific IP address
        self.rule = network.SecurityRule(
            f"pulumi-nsg-rule-{index}",
            network_security_group_name=self.nsg.name,
            resource_group_name=self.resource_group.name,
            priority=100,
            direction='Inbound',
            access='Allow',
            protocol='Tcp',
            source_port_range='*',
            destination_port_range='*',
            source_address_prefix=self.get_public_ip(),
            destination_address_prefix='*',
            description='Allow inbound traffic from a specific IP')

        # Create a Virtual Network and Subnet, associating the NSG with the subnet
        self.vnet = network.VirtualNetwork(
            f'pulumi-vnet-{index}',
            resource_group_name=self.resource_group.name,
            address_space=network.AddressSpaceArgs(
                address_prefixes=['10.0.0.0/16'],
            )
        )

        self.subnet = network.Subnet(
            f'pulumi-subnet-{index}',
            resource_group_name=self.resource_group.name,
            virtual_network_name=self.vnet.name,
            address_prefix='10.0.0.0/24',
            network_security_group=self.nsg
        )

        # Create a network profile for the container instance
        self.network_profile = network.NetworkProfile(
            f"pulumi-net-profile-{index}",
            resource_group_name=self.resource_group.name,
            container_network_interface_configurations=[network.ContainerNetworkInterfaceConfigurationArgs(
                name=f'pulumi-container-nic-config-{index}',
                ip_configurations=[network.IPConfigurationProfileArgs(
                    name=f'pulumi-ip-config-{index}',
                    subnet=network.SubnetArgs(
                        id=self.subnet.id
                    )
                )]
            )]
        )


        pulumi.log.info(f"Starting container: {container_name}")
        
        container_group_name = f"pulumi-containergroup-{container_name}-{index}"
        
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
                ports=[
                    containerinstance.PortArgs(
                        protocol="TCP", 
                        port=p
                        ) for p in ports
                ],
                type="Public",
                dns_name_label=f"{container_name}{DNS_LABEL}", # optional
            ),
            restart_policy="OnFailure",
            opts=pulumi.ResourceOptions(depends_on=[self.task])
        )

        # Construct the FQDN
        fqdn = pulumi.Output.all(container_group.name, container_group.location).apply(
            lambda args: f"{container_name}{DNS_LABEL}.{args[1]}.azurecontainer.io"
        )
        index += 1
        return fqdn
