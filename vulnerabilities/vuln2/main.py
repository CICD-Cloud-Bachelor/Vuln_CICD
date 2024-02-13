import pulumi
import pulumi_azure as azure
from pulumi_azure_native import authorization 
from source.create_azure_devops import CreateAzureDevops
from source.users_groups import UserCreator, GroupCreator

def start(resource_group):

    project_name = "Vulnerability_2"
    project_descrition = "Test for å lage wiki"
    organization_name = "bachelor2024"
    
    devops_username = "Ola_Nordmann"
    devops_password = "Passw0rd123"
    group_name = "Vulnerability_2_Group"
    

    azure_devops = CreateAzureDevops(project_name, project_descrition, organization_name, resource_group)
    
    devops_user = UserCreator.create_devops_user(devops_username, devops_password)
    custom_group = GroupCreator.create_group(azure_devops.project, group_name)
    GroupCreator.add_user_to_group(devops_user, custom_group)
    GroupCreator.modify_project_permission(azure_devops.project, custom_group, permissions = {"GENERIC_WRITE": "Allow",
                                                                                              "GENERIC_READ": "Allow"})

    azure_devops.create_work_item(count=10)


    

    