import pulumi
from faker import Faker
import pulumi_azure as azure
from source.create_azure_devops import CreateAzureDevops
from source.users_groups import UserCreator, GroupCreator
import configparser  

def vulnerble_part(azure_devops, config):
    
    faker = Faker()

    it_department_username = "IT_Department"
    it_departemnt_password = "##&#ssKKJnklss883630s"
    it_department_group_name = "IT_Department_Group"

    vuln_username = faker.name().replace(" ", "_")  
    vuln_password = "starter_password_1234"
    vuln_name = "Vulnerability_2_Group"

    work_item_title = "Important - create the new user to project"
    work_item_description = f"We need to add a new user to the important project. The user name is {vuln_username}."
                                
    work_item_comment = ["Set the password to the new user as the standar password for new users so the user can change it later."]

    azure_devops.add_user(it_department_username, it_departemnt_password)
    azure_devops.add_group(it_department_group_name)
    azure_devops.add_user_to_group(azure_devops.users.get(it_department_username), azure_devops.groups.get(it_department_group_name))
    azure_devops.modify_project_permission(azure_devops.groups.get(it_department_group_name), permissions = {"GENERIC_READ": "Allow",
                                                                                                            "GENERIC_WRITE": "Allow",
                                                                                                            "WORK_ITEM_READ": "Allow",
                                                                                                            "WORK_ITEM_WRITE": "Allow"
                                                                                                            })
    azure_devops.modify_area_permission(azure_devops.groups.get(it_department_group_name), permissions = {"GENERIC_READ": "Allow",
                                                                                                    "GENERIC_WRITE": "Allow",
                                                                                                    "WORK_ITEM_MOVE": "Allow",
                                                                                                    "WORK_ITEM_WRITE": "Allow"
                                                                                                    })

    devops_user = azure_devops.add_user(vuln_username, vuln_password)
    azure_devops.add_group(vuln_name)
    azure_devops.add_user_to_group(azure_devops.users.get(vuln_username), azure_devops.groups.get(vuln_name))
    azure_devops.modify_project_permission(azure_devops.groups.get(vuln_name), permissions = {"GENERIC_WRITE": "Allow",
                                                                                              "GENERIC_READ": "Allow",
                                                                                              "WORK_ITEM_READ": "Allow",
                                                                                              "WORK_ITEM_WRITE": "Allow"
                                                                                              })
    azure_devops.modify_area_permission(azure_devops.groups.get(vuln_name), permissions = {"GENERIC_READ": "Allow",
                                                                                            "GENERIC_WRITE": "Allow",
                                                                                            "WORK_ITEM_MOVE": "Allow",
                                                                                            "WORK_ITEM_WRITE": "Allow"
                                                                                                                    })

    azure_devops.create_work_item(
        type = "Task",
        title = work_item_title,
        assigned_to = f"{it_department_username}@{config['AZURE']['DOMAIN']}",
        description = work_item_description,
        comments = work_item_comment,
        depends_on = [azure_devops.project]
        )
    
    azure_devops.create_wiki("IT_Department")

    azure_devops.create_wiki_page("IT_Department", "IT_Department", "This is a page for the IT Deprtment\ testetst")

def start():

    resource_group = azure.core.ResourceGroup('resource-group', location="West Europe")
    
    config = configparser.ConfigParser()

    config.read('config.ini')

    project_name = "Vulnerability_2"
    project_descrition = "Test for å lage wiki"
    organization_name = config["AZURE"]["ORGANIZATION_NAME"]

    azure_devops = CreateAzureDevops(project_name, project_descrition, organization_name, resource_group)

    vulnerble_part(azure_devops, config)



    

    