import pulumi_azure as azure
import pulumi_azuredevops as azuredevops
from source.create_azure_devops import CreateAzureDevops
from source.container import DockerACR
from source.config import ORGANIZATION_NAME

PROJECT_NAME = "VULN4"
PROJECT_DESCRIPTION = "Project for VULN4"
GITHUB_REPO_URL = "https://github.com/CICD-Cloud-Bachelor/VULN4.git"
REPO_NAME = "VULN4_REPO"
PIPELINE_NAME = "pipeline"
IMAGE_NAME = "mysqldb"

CHALLENGE_DESCRIPTION = """
This challenge introduces artifacts. The challenge contains a repository and a pipeline that deploys a MySQL database. The pipeline contains connection details to the database. The flag is the password for the user "Troll_Trollington" wrapped with "FLAG{}".
"""
CHALLENGE_CATEGORY = "Medium"
FLAG = "FLAG{princess}"

def start(
        resource_group: azure.core.ResourceGroup,
        devops_user: azuredevops.User,
        acr: DockerACR
    ):

    connection_string = acr.start_container(
        image_name=IMAGE_NAME,
        ports=[3306], 
        cpu=1.0, 
        memory=1.0
    )

    azure_devops = CreateAzureDevops(
        project_name=PROJECT_NAME, 
        description=PROJECT_DESCRIPTION, 
        organization_name=ORGANIZATION_NAME, 
        resource_group=resource_group
    )

    azure_devops.create_wiki_with_content(
        wiki_name="VULN4WIKI",
        page_name="Dev",
        markdown_file_path="templates/wiki_pages/vuln4.md"
    )

    azure_devops.import_github_repo(
        github_repo_url=GITHUB_REPO_URL, 
        repo_name=REPO_NAME,
        is_private=False
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
        run=False
    ) 

    group = azure_devops.add_group(
        group_name="Custom Group"
    )
    
    azure_devops.add_user_to_group(
        user=devops_user,
        group=group
    )
    azure_devops.add_user_to_default_group(
        user=devops_user,
        default_group_name="Readers"
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
            "QueueBuilds": "Allow",
            "ManageBuildQueue": "Allow",
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
    azure_devops.modify_area_permissions(
        group=group,
        permissions={
            "GENERIC_READ": "Allow",
            "GENERIC_WRITE": "Allow",
            "WORK_ITEM_READ": "Allow"  
        }
    )
    
    azure_devops.create_work_item(
        type="Task",
        title="Investigate production outage",
        description="Investigate production outage",
        assigned_to=devops_user.principal_name,
        comments=[
            "Investigating",
            "Fixed" 
        ],
        depends_on=[devops_user, azure_devops.project]
    )
    
    azure_devops.generate_random_work_items(
        assigned_to=devops_user.principal_name,
        amount=10,
        file_path="templates/work_items/work_item_dataset.json"
    )