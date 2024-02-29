import pulumi
import pulumi_azure as azure
from source.create_azure_devops import CreateAzureDevops
from source.users_groups import UserCreator, GroupCreator
import configparser  

def vulnerble_part(azure_devops, config):
    devops_username = "Ola_Nordmann20"
    devops_password = "Passw0rd123"
    group_name = "Vulnerability_2_Group"

    devops_user = azure_devops.add_user(devops_username, devops_password)
    azure_devops.create_group(azure_devops.project, azure_devops.users.get(devops_username))
    azure_devops.add_user_to_group(devops_user, azure_devops.groups.get(group_name))
    azure_devops.modify_project_permission(azure_devops.project, azure_devops.groups.get(group_name), permissions = {"GENERIC_WRITE": "Allow",
                                                                                              "GENERIC_READ": "Allow",
                                                                                              "WORK_ITEM_MOVE": "Allow",
                                                                                              "WORK_ITEM_DELETE": "Allow"
                                                                                              })
    azure_devops.modify_area_permissions(azure_devops.project, azure_devops.groups.get(group_name), permissions = {"GENERIC_READ": "Allow",
                                                                                            "GENERIC_WRITE": "Allow",
                                                                                            "WORK_ITEM_READ": "Allow",
                                                                                            "WORK_ITEM_WRITE": "Allow"
                                                                                                                    })
    azure_devops.create_work_item(
        type = "Epic",
        title = "En testepic",
        assigned_to = f"{devops_username}@{config['AZURE']['DOMAIN']}",
        description = "Gi bruker nytt passord",
        comments = ["Dette er en kommentar"],
        depends_on = [azure_devops.project, devops_user]
        )

def start():

    resource_group = azure.core.ResourceGroup('resource-group', location="West Europe")
    
    config = configparser.ConfigParser()

    config.read('config.ini')

    project_name = "Vulnerability_2"
    project_descrition = "Test for å lage wiki"
    organization_name = config["AZURE"]["ORGANIZATION_NAME"]

    azure_devops = CreateAzureDevops(project_name, project_descrition, organization_name, resource_group)

    vulnerble_part(azure_devops, config)

    #azure_devops.create_work_item("Epic", "En testepic", "")



    

    