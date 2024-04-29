import pulumi
import pulumi_azure as azure
import pulumi_azuredevops as azuredevops
from faker import Faker
from source.create_azure_devops import CreateAzureDevops
from source.config import *

faker = Faker()

PROJECT_NAME = "Vulnerability 3"
PROJECT_DESCRIPTION = "Insufficient Credential Hygiene"
GROUP_NAME = "Reduced_Permissions_Group"
GITHUB_REPO_URL = "https://github.com/CICD-Cloud-Bachelor/VULN3.git"
REPO_NAME = "python-calculator"
PIPELINE_NAME = "Run unit tests"

CHALLENGE_DESCRIPTION = """
Credentials... Hold them safe, or else you might have to look for a needle in a haystack
"""
CHALLENGE_CATEGORY = "Easy"
FLAG = "FLAG{AAAAB3NzaC1yc2EAAAABIwAAAQEAq2A7hRGmdnm9tUDbO9IDSwBK6TbQa}"

def start(resource_group: azure.core.ResourceGroup, devops_user: azuredevops.User):

    devops_project = CreateAzureDevops(
        PROJECT_NAME,
        PROJECT_DESCRIPTION,
        ORGANIZATION_NAME,
        resource_group
    )

    devops_project.import_github_repo(
        GITHUB_REPO_URL, 
        REPO_NAME,
        is_private=False
    )

    devops_project.create_pipeline(
        PIPELINE_NAME,
        run=False,
        branch="dev"
    )

    custom_group = devops_project.add_group(GROUP_NAME)
    
    devops_project.add_user_to_group(
        devops_user, 
        custom_group
    )

    # Give custom_group read permissions to the devops project
    devops_project.modify_project_permissions(
        custom_group,
        permissions = {
            "GENERIC_READ": "Allow"
        }
    )

    devops_project.modify_repository_permissions(
        custom_group,
        permissions = {
            "GenericRead": "Allow"
        }
    )
