import pulumi_azure as azure
from source.create_azure_devops import CreateAzureDevops
from source.container import DockerACR
from faker import Faker
from source.config import ORGANIZATION_NAME

faker = Faker()

PROJECT_NAME = "VULN4"
PROJECT_DESCRIPTION = "Project for VULN4"
GITHUB_REPO_URL = "https://github.com/CICD-Cloud-Bachelor/VULN4.git"
REPO_NAME = "VULN4_REPO"
PIPELINE_NAME = "testpipeline"
IMAGE_NAME = "mysqldb"

CHALLENGE_DESCRIPTION = """
Dette er fjerde challenge jippi!!
Den er veldig morro og du kommer til å like den
Denne er veldig enkel
"""
CHALLENGE_CATEGORY = "Medium"

def start(resource_group: azure.core.ResourceGroup):
    acr = DockerACR(
        resource_group=resource_group, 
    )

    connection_string = acr.start_container(
        image_name=IMAGE_NAME,
        ports=[3306], 
        cpu=1.0, 
        memory=1.0
    )
    #import pulumi
    #pulumi.export("connection_string", connection_string)   
    
    azure_devops = CreateAzureDevops(
        project_name=PROJECT_NAME, 
        description=PROJECT_DESCRIPTION, 
        organization_name=ORGANIZATION_NAME, 
        resource_group=resource_group
    )

    azure_devops.create_wiki(
        wiki_name="VULN4_WIKI"
    )

    azure_devops.create_wiki_page(
        wiki_name="VULN4_WIKI",
        page_name="Dev",
        markdown_file_path="vulnerabilities/vuln4/fake_wiki/fake_wiki.md"
    )

    azure_devops.import_github_repo(
        github_repo_url=GITHUB_REPO_URL, 
        repo_name=REPO_NAME
    )

    azure_devops.create_pipeline(
        name=PIPELINE_NAME,
        variables={
            "CONNECTION_STRING": connection_string, 
            "DATABASE": "prod", 
            "USERNAME": "root", 
            "PASSWORD": "myr00tp455w0rd"
        },
        branch="main",
        #run=True
    ) 

    group = azure_devops.add_group(
        group_name="Custom Group"
    )
    user = azure_devops.add_user(
        name=faker.name().replace(".", ""),
        password="Troll57Hoho69%MerryChristmas"
    )
    azure_devops.add_user_to_group(
        user=user,
        group=group
    )

    users = [
        azure_devops.add_user(
            name=faker.name().replace(".", "")
        ) for _ in range(2)
    ]

    for user in users:
        azure_devops.add_user_to_group(
            user=user,
            group=group
        )

    azure_devops.modify_project_permissions(
        group=group, 
        permissions={
            "GENERIC_READ": "Allow",
        }
    )
    azure_devops.modify_pipeline_permissions(
        group=group, 
        permissions={
            "ViewBuilds": "Allow",
            "ViewBuildDefinition": "Allow"
        }
    )
    azure_devops.modify_repository_permissions(
        group=group, 
        permissions={
            "GenericRead": "Allow"
        }
    )
    
    azure_devops.create_work_item(
        type="Task",
        title="Investigate production outage",
        description="Investigate production outage",
        assigned_to=user.principal_name,
        comments=[
            "Investigating",
            "Fixed" 
        ],
        depends_on=[user, azure_devops.project]
    )
  