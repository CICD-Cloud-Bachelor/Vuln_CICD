import pulumi_azure as azure
import pulumi_azuredevops as azuredevops
from source.create_azure_devops import CreateAzureDevops
from source.config import ORGANIZATION_NAME


PROJECT_NAME = "VULN1"
PROJECT_DESCRIPTION = "Project for VULN1"
GITHUB_REPO_URL = "https://github.com/CICD-Cloud-Bachelor/VULN1.git"
REPO_NAME = "VULN1_REPO"
PIPELINE_NAME = "BUILD_PIPELINE"

CHALLENGE_DESCRIPTION = """
This challenge contains a repository and a pipeline that builds the code in the repository. The pipeline has a secret flag that is used during the build process. Your task is to retrieve the flag.
"""
CHALLENGE_CATEGORY = "Easy"
FLAG = "FLAG{you_were_not_supposed_to_find_this}"

def start(
        resource_group: azure.core.ResourceGroup, 
        devops_user: azuredevops.User
    ):
    azure_devops = CreateAzureDevops(
        project_name=PROJECT_NAME, 
        description=PROJECT_DESCRIPTION, 
        organization_name=ORGANIZATION_NAME,
        resource_group=resource_group
    )

    azure_devops.import_github_repo(
        github_repo_url=GITHUB_REPO_URL, 
        repo_name=REPO_NAME,
        is_private=False
    )

    azure_devops.create_pipeline(
        name=PIPELINE_NAME,
        variables={
            "FLAG": FLAG
        },
        branch="main",
        run=True
    ) 

    group = azure_devops.add_group(
        group_name="Custom Group"
    )
    
    azure_devops.add_user_to_group(
        user=devops_user,
        group=group
    )

    azure_devops.modify_project_permissions(
        group=group, 
        permissions={
            "GENERIC_READ": "Allow",
            "GENERIC_WRITE": "Allow",
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
            "GenericContribute": "Allow",
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

    azure_devops.create_wiki_with_content(
        wiki_name="VULN1WIKI",
        page_name="VULN1CHALLENGE",
        markdown_file_path="templates/wiki_pages/vuln1.md"
    )

    azure_devops.generate_random_work_items(
        assigned_to=devops_user.principal_name,
        amount=10,
        file_path="templates/work_items/work_item_dataset.json"
    )