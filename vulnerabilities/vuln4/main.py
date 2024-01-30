import pulumi_azure as azure
from source.add_users import CreateUsers
from source.create_azure_devops import CreateAzureDevops
from source.container import CreateContainer, ImportDockerImageToACR



def start(resource_group: azure.core.ResourceGroup):
    acr = ImportDockerImageToACR(resource_group, "mysqldb")
    string = acr.build_and_push_docker()

    