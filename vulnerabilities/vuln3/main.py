import pulumi
import pulumi_azure as azure
import configparser
from faker import Faker
from source.create_azure_devops import CreateAzureDevops

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

def start(resource_group: azure.core.ResourceGroup):

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

    low_privil_user = devops_project.add_user(
        low_privil_username,
        DEVOPS_USER1_PASSWORD
    )

    custom_group = devops_project.add_group(GROUP_NAME)
    
    devops_project.add_user_to_group(
        low_privil_user, 
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

