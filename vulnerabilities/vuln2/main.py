import pulumi
from faker import Faker
import pulumi_azure as azure
import random as ra
from source.create_azure_devops import CreateAzureDevops
from source.users_groups import UserCreator, GroupCreator
import configparser  

def generate_users(azure_devops):
    
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
    vuln_name = "Vulnerability_2_Group"

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
                                                                                                    "WORK_ITEM_READ": "Allow",
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
                                                                                            "WORK_ITEM_READ": "Allow",
                                                                                            "WORK_ITEM_WRITE": "Allow"
                                                                                                                    })

def generate_wiki_page(azure_devops):
    
    azure_devops.create_wiki("IT_Department")

    with open("vulnerabilities/vuln2/wiki_page.md", "r") as file:
        azure_devops.create_wiki_page("IT_Department", "IT_Department", file.read())


def generate_work_items(azure_devops):
    work_item_title = "Important - create the new user to project"
    work_item_description = f"We need to add a new user to the important project. The user name is {vuln_username}."
                                
    work_item_comment = ["Set the password in accordance with the IT department's policy, as usual."]

    templates = [
        "Cannot access Azure Virtual Machine named {resource_name}.",
        "Experiencing latency issues with Azure {service_name}.",
        "{resource_name} failed to deploy.",
        "Need additional permissions in Azure Active Directory for {user_role}.",
        "How do I configure {service_name} for high availability?",
        "Requesting increase in quota for {service_name}.",
        "Azure {service_name} is showing unexpected charges.",
        "Connectivity issues between Azure VPN Gateway and {resource_name}.",
        "Data recovery needed for Azure Blob Storage account named {resource_name}.",
        "Trouble setting up Azure AD Connect for {resource_name}."
    ]
    
    # Words to fill into the templates
    service_names = ["Virtual Networks", "SQL Database", "Function App", "Kubernetes Service", "Blob Storage"]
    resource_names = ["ResourceGroup1", "MyAzureVM", "StorageAccount", "SQLServerDB", "WebAppService"]
    user_roles = ["developer", "project manager", "data scientist", "system administrator", "network engineer"]

    for i in range(10):
        
        description = azure_devops.generate_fake_text(templates, service_names, resource_names, user_roles)
        tile = f"{description.split()[0]} issue"

        pulumi.debug(f"{description}")

        azure_devops.create_work_item(
            type = "Task",
            title = tile,
            assigned_to = f"{it_department_username}@{config['AZURE']['DOMAIN']}",
            description = description,
            comments = [None],
            depends_on = [azure_devops.project]
            )

    azure_devops.create_work_item(
        type = "Task",
        title = work_item_title,
        assigned_to = f"{it_department_username}@{config['AZURE']['DOMAIN']}",
        description = work_item_description,
        comments = work_item_comment,
        depends_on = [azure_devops.project]
        )

def start():

    global config

    resource_group = azure.core.ResourceGroup('resource-group', location="West Europe")
    
    config = configparser.ConfigParser()

    config.read('config.ini')

    project_name = "Vulnerability_2"
    project_descrition = "Test for å lage wiki"
    organization_name = config["AZURE"]["ORGANIZATION_NAME"]

    azure_devops = CreateAzureDevops(project_name, project_descrition, organization_name, resource_group)

    generate_users(azure_devops)

    generate_work_items(azure_devops)

    generate_wiki_page(azure_devops)



    

    