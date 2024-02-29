import pulumi
import pulumi_azure as azure
import pulumi_azuread as azuread
import pulumi_azuredevops as azuredevops
import configparser
from source.users_groups import UserCreator, GroupCreator
from source.create_azure_devops import CreateAzureDevops
from source.container import CreateContainer
from faker import Faker

faker = Faker()
config = configparser.ConfigParser()
config.read('config.ini')
ORGANIZATION_NAME = config["AZURE"]["ORGANIZATION_NAME"]

PROJECT_NAME = "Vulnerability 3"
PROJECT_DESCRIPTION = "Insufficient Credential Hygiene"
GROUP_NAME = "Custom Permissions Group"
GITHUB_REPO_URL = "https://github.com/flis5/svakhet3.git"
REPO_NAME = "Vulnerability_3"
PIPELINE_NAME = "Vulnerability-3-CICD-Pipeline"
DEVOPS_USER1_PASSWORD = "Troll57Hoho69%MerryChristmas"

def start():
    resource_group = azure.core.ResourceGroup('resource-group', location="West Europe")

    create_devops = CreateAzureDevops(
        PROJECT_NAME,
        PROJECT_DESCRIPTION,
        ORGANIZATION_NAME,
        resource_group
    )

    create_devops.import_github_repo(
        GITHUB_REPO_URL, 
        REPO_NAME
    )

    vuln3_pipeline = create_devops.create_ci_cd_pipeline(PIPELINE_NAME)

    devops_user = UserCreator.create_devops_user(
        faker.name().replace('.', ' '),
        DEVOPS_USER1_PASSWORD
    )

    custom_group = GroupCreator.create_group(
        create_devops.project, 
        GROUP_NAME
    )
    
    GroupCreator.add_user_to_group(
        devops_user, 
        custom_group
    )

    # Give custom_group read permissions to the devops project
    GroupCreator.modify_project_permission(
        create_devops.project, 
        custom_group,
        permissions = {
            "GENERIC_READ": "Allow"
        }
    )

    GroupCreator.modify_repository_permissions(
        create_devops.project,
        custom_group,
        create_devops.git_repo,
        permissions = {
            "GenericRead": "Allow"
        }
    )

    # Contribute permissions on dev branch
    GroupCreator.modify_branch_permissions(
        create_devops.project,
        custom_group,
        create_devops.git_repo,
        "refs/heads/dev",
        permissions = {
            "GenericContribute": "Allow"
        }
    )

    # Allow custom_group to run pipelines
    GroupCreator.modify_pipeline_permissions(
        create_devops.project,
        custom_group,
        vuln3_pipeline,
        permissions = {
            "QueueBuilds": "Allow",
            "ViewBuilds": "Allow", # Required to view the finished runs of the pipeline
            "ViewBuildDefinition": "Allow" # Required to view the pipeline
        }
    )

    user_john = create_devops.users.get("")
