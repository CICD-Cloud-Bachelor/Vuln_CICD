import pulumi_azure as azure
from source.add_users import CreateUsers
from source.create_azure_devops import CreateAzureDevops
from source.container import CreateContainer, DockerACR



def start(resource_group: azure.core.ResourceGroup):
    acr = DockerACR(resource_group, "registrypulumi")
    acr_string = acr.build_and_push_docker_image("mysqldb")

    acr.start_container(acr_string, "mysql-container", 3306, 1.0, 1.0)
