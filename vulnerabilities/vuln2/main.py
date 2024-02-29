import pulumi
import pulumi_azure as azure
from source.create_azure_devops import CreateAzureDevops
from source.users_groups import UserCreator, GroupCreator
from source.workitem import WorkItem
import configparser  

def start():

    resource_group = azure.core.ResourceGroup('resource-group', location="West Europe")
    
    config = configparser.ConfigParser()

    config.read('config.ini')

    project_name = "Vulnerability_2"
    project_descrition = "Test for å lage wiki"
    organization_name = config["AZURE"]["ORGANIZATION_NAME"]

    azure_devops = CreateAzureDevops(project_name, project_descrition, organization_name, resource_group)

    work_item = WorkItem(organization_name, project_name, resource_group)

    work_item.create("Task", "Task 1", "Description 1", "Comment 1")
    
    #devops_username = "Ola_Nordmann6"
    #devops_password = "Passw0rd123"
    #group_name = "Vulnerability_2_Group"
    #
    #devops_user = UserCreator.create_devops_user(devops_username, devops_password)
    #custom_group = GroupCreator.create_group(azure_devops.project, group_name)
    #GroupCreator.add_user_to_group(devops_user, custom_group)
    #GroupCreator.modify_project_permission(azure_devops.project, custom_group, permissions = {"GENERIC_WRITE": "Allow",
    #                                                                                          "GENERIC_READ": "Allow",
    #                                                                                          "WORK_ITEM_MOVE": "Allow",
    #                                                                                          "WORK_ITEM_DELETE": "Allow"
    #                                                                                          })
    #GroupCreator.modify_area_permissions(azure_devops.project, custom_group, permissions = {"GENERIC_READ": "Allow",
    #                                                                                        "GENERIC_WRITE": "Allow",
    #                                                                                        "WORK_ITEM_READ": "Allow",
    #                                                                                        "WORK_ITEM_WRITE": "Allow"
    #                                                                                                                })
    #azure_devops.create_work_item(count=10)


    

    