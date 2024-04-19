import pulumi
from faker import Faker
import pulumi_azure as azure
import random as ra
from source.create_azure_devops import CreateAzureDevops
import configparser  
from source.container import DockerACR

CHALLENGE_DESCRIPTION = """
Dette er andre challenge jippi!!
Den er veldig morro og du kommer til å like den
Denne er veldig enkel
"""

def generate_users(azure_devops, vuln_azure_devops):
    
    global vuln_username
    global it_department_username

    faker = Faker()

    it_department_username = f"IT_Department_Account{ra.randint(1, 1000)}"
    it_departemnt_password = "##&#ssKKJnklss883630s"
    it_department_group_name = "IT_Department_Group"
    
    it_user = azure_devops.add_user(
        name=it_department_username,
        password=it_departemnt_password
        )
    it_group = azure_devops.add_group(
        group_name=it_department_group_name
        )   
    azure_devops.add_user_to_group(
        user=it_user,
        group=it_group
        )
    azure_devops.modify_project_permissions(
        group=it_group, 
        permissions = {"GENERIC_READ": "Allow",
                        "GENERIC_WRITE": "Allow"
                        })
                                                                                                   
    vuln_username = faker.name().replace(" ", "_")  
    vuln_password = "Complex!Start2024$PassW0rd#"
    vuln_group_name = "Vulnerability_2_Group"

    vuln_user = vuln_azure_devops.add_user(
        name=vuln_username,
        password=vuln_password
        )

    vuln_group = vuln_azure_devops.add_group(
        group_name=vuln_group_name
        )
    
    vuln_azure_devops.add_user_to_default_group(
        user=vuln_user,
        default_group_name="Readers"
        )

    vuln_azure_devops.add_user_to_group(
        user=vuln_user,
        group=vuln_group
        )

    vuln_azure_devops.modify_project_permissions(
        group=vuln_group,
        permissions = {"GENERIC_READ": "Allow",
                        "GENERIC_WRITE": "Allow"
                        })
    
    vuln_azure_devops.modify_area_permissions(
        group=vuln_group,
        permissions= {"GENERIC_READ": "Allow",
                      "GENERIC_WRITE": "Allow",
                      "WORK_ITEM_READ": "Allow"  
                        })

    vuln_azure_devops.modify_pipeline_permissions(
        group=vuln_group,
        permissions = {"ViewBuilds": "Allow"}
        )

def generate_wiki_page(azure_devops, vuln_azure_devops):

    ##Understrek på navnet er muligens feil
    azure_devops.create_wiki_with_content(
        wiki_name="IT_Department_Wiki",
        page_name="IT_Department",
        markdown_file_path="templates/wiki_pages/wiki_page_vuln2_IT.md"
        )

    vuln_azure_devops.create_wiki_with_content(
        wiki_name="Super_Secret_Wiki",
        page_name="Super_Secret",
        markdown_file_path="templates/wiki_pages/wiki_page_vuln2_Secret_Project.md")

def generate_work_items_IT(azure_devops):
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
    
    azure_devops.generate_random_work_items(
        assigned_to=f"{it_department_username}@{config['AZURE']['DOMAIN']}",
        amount=60,
    )

    work_item_title = "Remove user from project"
    work_item_description = f"We need to remove the user {vuln_username} from the the important project. This is due that the user has finished the job."
                                
    azure_devops.create_work_item(
        type = "Task",
        title = work_item_title,
        assigned_to = f"{it_department_username}@{config['AZURE']['DOMAIN']}",
        description = work_item_description,
        comments = []
        )
    
    azure_devops.generate_random_work_items(
        assigned_to=f"{it_department_username}@{config['AZURE']['DOMAIN']}",
        amount=38,
    )

def generate_work_items_vuln(vuln_azure_devops):

    vuln_azure_devops.create_work_item(
        type = "Task",
        title = "Important - Fix Pipeline",
        assigned_to = None,
        description = """We need to fix the pipeline as it is not working properly.
                        The pipeline is used to deploy the application to the production environment. 
                        This pipeline will be deploy the admin panel to 20.000 customers tomorrow!""",
        state="Active",
        comments = []
        ) 

    vuln_azure_devops.create_work_item(
        type = "Task",
        title = "Important - 1 day left to deploy",
        assigned_to = None,
        description = f"""There is 1 day left to deploy the admin panel.
                          I have set up a azure web series to host the application.
                          The URL is http://{IMAGENAME}{config['DOCKER']['DNS_LABEL']}.{config['AZURE']['LOCATION']}.azurecontainer.io.""",            
        state="Active",
        comments = [],
        depends_on = []
        )


def import_gitrepo_to_project(azure_devops, vuln_azure_devops):

        azure_devops.import_github_repo(
            github_repo_url="https://github.com/CICD-Cloud-Bachelor/VULN2_IT.git",
            repo_name="IT Department Ticket Development",
            is_private=False
        )

        vuln_azure_devops.import_github_repo(
            github_repo_url="https://github.com/CICD-Cloud-Bachelor/VULN2_Secret.git",
            repo_name="Super Secret Admin Panel",
            is_private=False
        )

def import_pipeline_to_project(azure_devops, vuln_azure_devops):
         
        azure_devops.create_pipeline(
            name="IT_Department_Pipeline",
            branch="dev",
            run=False
        )
    
        vuln_azure_devops.create_pipeline(
            name="Super_Secret_Pipeline",
            branch="dev",
            run=False
        )

def init_docker_acr(resource_group):
    
    global IMAGENAME

    IMAGENAME = "bestadminpanel"

    acr = DockerACR(
        resource_group=resource_group, 
    )

    url = acr.start_container(
        image_name=IMAGENAME,
        ports=[80],
        cpu=1.0,
        memory=1.0
    )

    pulumi.export("URL", url)

def start(resource_group):

    global config
    
    config = configparser.ConfigParser()

    config.read('config.ini')
    
    project_name = "IT_Department"
    project_descrition = "Project for the IT department to manage development and handle tickets. Much better than Jira."
    organization_name = config["AZURE"]["ORGANIZATION_NAME"]

    azure_devops = CreateAzureDevops(
        project_name=project_name, 
        description=project_descrition, 
        organization_name=organization_name, 
        resource_group=resource_group
        )

    vuln_project_name = "Super_Secret_Project"
    vuln_project_description = "This project is so secret that not even the IT department should know about it."

    vuln_azure_devops = CreateAzureDevops(
        project_name=vuln_project_name,
        description=vuln_project_description, 
        organization_name=organization_name,
        resource_group=resource_group
        )

    import_gitrepo_to_project(azure_devops, vuln_azure_devops)

    import_pipeline_to_project(azure_devops, vuln_azure_devops)

    generate_users(azure_devops, vuln_azure_devops)

    generate_work_items_IT(azure_devops)

    generate_wiki_page(azure_devops, vuln_azure_devops)

    init_docker_acr(resource_group)

    generate_work_items_vuln(vuln_azure_devops)

 
        

    


    

    