import pulumi_azure as azure
import pulumi_azuredevops as azuredevops
from source.create_azure_devops import CreateAzureDevops
from source.container import DockerACR
from source.config import *

PROJECT_NAME = "VULNX"
PROJECT_DESCRIPTION = "Project for VULNX"
GITHUB_REPO_URL = "https://github.com/CICD-Cloud-Bachelor/VULN4.git" # the URL of the repository to be imported in the Azure DevOps project
REPO_NAME = "VULNX_REPO"
PIPELINE_NAME = "samplepipeline"
IMAGE_NAME = "docker_image_folder_name" # the name of the folder in the CONTAINER_PATH config, containing the Dockerfile

CHALLENGE_DESCRIPTION = """
Sample description
"""
CHALLENGE_CATEGORY = "Medium" # Easy, Medium, or Hard
FLAG = "FLAG{tempflag}"



def start(
        resource_group: azure.core.ResourceGroup,
        devops_user: azuredevops.User,
        acr: DockerACR # to be used if the vulnerability requires a container registry
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
        is_private=False # this is not functional at the moment
    )

    azure_devops.create_pipeline(
        name=PIPELINE_NAME,
        variables={
            "VARIABLE_NAME": "VARIABLE_VALUE",
            "VARIABLE_NAME2": "VARIABLE_VALUE2",
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

    azure_devops.modify_project_permissions(
        group=group, 
        permissions={
            "GENERIC_READ": "Allow",
        }
    )