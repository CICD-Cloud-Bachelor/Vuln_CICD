import pulumi
from faker import Faker
import pulumi_azure as azure
import random as ra
from source.create_azure_devops import CreateAzureDevops
from source.users_groups import UserCreator, GroupCreator
import configparser  

def generate_users(azure_devops, vuln_azure_devops):
    
    global vuln_username
    global vuln_password
    global it_department_username
    global it_departemnt_password

    faker = Faker()

    it_department_username = f"IT_Department{ra.randint(1, 1000)}"
    it_departemnt_password = "##&#ssKKJnklss883630s"
    it_department_group_name = "IT_Department_Group"

    vuln_username = faker.name().replace(" ", "_")  
    vuln_password = "Complex!Start2024$PassW0rd#"
    vuln_group = "Vulnerability_2_Group"
    
    azure_devops.add_user(it_department_username, it_departemnt_password)
    azure_devops.add_group(it_department_group_name)
    azure_devops.add_user_to_group(azure_devops.users.get(it_department_username), azure_devops.groups.get(it_department_group_name))
    azure_devops.modify_project_permissions(azure_devops.groups.get(it_department_group_name), permissions = {"GENERIC_READ": "Allow",
                                                                                                              "GENERIC_WRITE": "Allow",
                                                                                                              "WORK_ITEM_MOVE": "Allow",
                                                                                                              "WORK_ITEM_DELETE": "Allow"
                                                                                                            })
    #azure_devops.modify_area_permissions(azure_devops.groups.get(it_department_group_name), permissions = {"GENERIC_READ": "Allow",
    #                                                                                                       "Generic_Write": "Allow",
    #                                                                                                       "WORK_ITEM_MOVE": "Allow"
    #                                                                                                        })    
    
    vuln_azure_devops.add_user(vuln_username, vuln_password)
    vuln_azure_devops.add_group(vuln_group)
    vuln_azure_devops.add_user_to_group(vuln_azure_devops.users.get(vuln_username), vuln_azure_devops.groups.get(vuln_group))
    vuln_azure_devops.modify_project_permissions(vuln_azure_devops.groups.get(vuln_group), permissions = {"GENERIC_WRITE": "Allow"
                                                                                              })
    vuln_azure_devops.modify_area_permissions(vuln_azure_devops.groups.get(vuln_group), permissions = {"GENERIC_READ": "Allow"
                                                                                                                    })

def generate_wiki_page(azure_devops, vuln_azure_devops):
    
    azure_devops.create_wiki("IT_Department")
    azure_devops.create_wiki_page("IT_Department", "IT_Department", "templates/wiki_pages/wiki_page_vuln2_IT.md")

    vuln_azure_devops.create_wiki("Super_Secret_Project")
    vuln_azure_devops.create_wiki_page("Super_Secret_Project", "Super_Secret_Project", "templates/wiki_pages/wiki_page_vuln2_Secret_Project.md")

def generate_work_items(azure_devops):
    work_item_title = "Important - create the new user to project"
    work_item_description = f"We need to add a new user to the important project. The user name is {vuln_username}."
                                
    work_item_comment = ["Set the password in accordance with the IT department's policy, as usual.", "Work item has been closed as this has been resolved."]

    azure_devops.create_work_item(
        type = "Task",
        title = work_item_title,
        assigned_to = f"{it_department_username}@{config['AZURE']['DOMAIN']}",
        description = work_item_description,
        comments = work_item_comment,
        state="Closed"
        )
    
    #azure_devops.generate_random_work_items(
    #    assigned_to=f"{it_department_username}@{config['AZURE']['DOMAIN']}",
    #    amount=60,
    #)

    work_item_title = "Remove user from project"
    work_item_description = f"We need to remove the user {vuln_username} from the the important project. This is due that the user has finished the job."
                                
    azure_devops.create_work_item(
        type = "Task",
        title = work_item_title,
        assigned_to = f"{it_department_username}@{config['AZURE']['DOMAIN']}",
        description = work_item_description,
        comments = []
        )
    
    #azure_devops.generate_random_work_items(
    #    assigned_to=f"{it_department_username}@{config['AZURE']['DOMAIN']}",
    #    amount=38,
    #)
    
def start():

    global config

    resource_group = azure.core.ResourceGroup('magnusme_resource-group', location="West Europe")
    
    config = configparser.ConfigParser()

    config.read('config.ini')

    project_name = "IT Department Project"
    project_descrition = "Project for the IT department to manage development and handle tickets. Much better than Jira."
    organization_name = config["AZURE"]["ORGANIZATION_NAME"]

    azure_devops = CreateAzureDevops(project_name, project_descrition, organization_name, resource_group)

    vuln_project_name = "Super Secret Project"
    vuln_project_description = "This project is so secret that not even the IT department should know about it."

    vuln_azure_devops = CreateAzureDevops(vuln_project_name, vuln_project_description, organization_name, resource_group)

    generate_users(azure_devops, vuln_azure_devops)

    generate_work_items(azure_devops)

    generate_wiki_page(azure_devops, vuln_azure_devops)

    


    

    