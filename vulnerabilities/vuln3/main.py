import pulumi
import pulumi_azure as azure
import pulumi_azuread as azuread
import pulumi_azuredevops as azuredevops
import configparser
from faker import Faker
from source.users_groups import UserCreator, GroupCreator
from source.create_azure_devops import CreateAzureDevops
from source.container import CreateContainer

faker = Faker()
config = configparser.ConfigParser()
config.read('config.ini')
ORGANIZATION_NAME = config["AZURE"]["ORGANIZATION_NAME"]

PROJECT_NAME = "Vulnerability 3"
PROJECT_DESCRIPTION = "Insufficient Credential Hygiene"
GROUP_NAME = "Custom Permissions Group"
GITHUB_REPO_URL = "https://github.com/flis5/svakhet3.git"
REPO_NAME = "python-calculator"
PIPELINE_NAME = "Run unit tests"
DEVOPS_USER1_PASSWORD = "Troll57Hoho69%MerryChristmas"

def start():
    resource_group = azure.core.ResourceGroup('resource-group', location="West Europe")

    devops_project = CreateAzureDevops(
        PROJECT_NAME,
        PROJECT_DESCRIPTION,
        ORGANIZATION_NAME,
        resource_group
    )

    devops_project.import_github_repo(
        GITHUB_REPO_URL, 
        REPO_NAME
    )

    devops_project.create_ci_cd_pipeline(PIPELINE_NAME)

    low_privil_username = faker.name().replace('.', ' ')

    devops_project.add_user(
        low_privil_username,
        DEVOPS_USER1_PASSWORD
    )

    devops_project.add_group(GROUP_NAME)
    
    GroupCreator.add_user_to_group(
        devops_project.users.get(low_privil_username), 
        devops_project.groups.get(GROUP_NAME)
    )

    # Give custom_group read permissions to the devops project
    GroupCreator.modify_project_permission(
        devops_project.project, 
        devops_project.groups.get(GROUP_NAME),
        permissions = {
            "GENERIC_READ": "Allow"
        }
    )

    GroupCreator.modify_repository_permissions(
        devops_project.project,
        devops_project.groups.get(GROUP_NAME),
        devops_project.git_repo,
        permissions = {
            "GenericRead": "Allow"
        }
    )

