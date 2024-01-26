import pulumi
import pulumi_azure as azure


class CreateContainer:
    resource_group = azure.core.ResourceGroup('myresourcegroup', location='WestUS2')
    
    def __init__(self, name: str, image: str, memory: float, port: int, cpu: int):
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
