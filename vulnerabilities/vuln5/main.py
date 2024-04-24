import pulumi_azure as azure
import pulumi_azuredevops as azuredevops
from source.create_azure_devops import CreateAzureDevops
from source.container import DockerACR
from source.config import *

PROJECT_NAME = "VULN5"
PROJECT_DESCRIPTION = "Project for VULN5"
GITHUB_REPO_URL = "https://github.com/CICD-Cloud-Bachelor/VULN5.git"
REPO_NAME = "VULN5_REPO"
PIPELINE_NAME = "testpipeline"
IMAGE_NAME1 = "ftpserver"
IMAGE_NAME2 = "ftppoller"

CHALLENGE_DESCRIPTION = """
This challenge simulates a complete pipeline from development to customer. The CI/CD pipeline builds and pushes code to a FTP server which works as a distributer to the customers. The customer automatically downloads and runs the file from the FTP server. Your task is to retrieve the flag file from the customer.
"""
CHALLENGE_CATEGORY = "Hard"
FLAG = "FLAG{pwned_the_customer}"

def start(
        resource_group: azure.core.ResourceGroup,
        devops_user: azuredevops.User,
        acr: DockerACR
    ):
    update_flag_file()
    original_file_contents = update_ftp_fqdn()

    connection_string = acr.start_container(
        image_name=IMAGE_NAME1,
        ports=[21] + [*range(40000, 40004)],
        cpu=1.0,
        memory=1.0
    )

    acr.start_container(
        image_name=IMAGE_NAME2,
        ports=[21],
        cpu=1.0,
        memory=1.0
    )
    revert_file_content(original_file_contents)

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
            "FTP_HOST": connection_string, 
            "FTP_USER": "ftpshared", 
            "FTP_PASS": "MAsds8ASDsadm82988"
        },
        branch="main",
        run=False
    )

    azure_devops.create_work_item(
        type="Task",
        title="Deploy FTP Server",
        description="Deploy the FTP server to the Azure Container Registry",
        comments=[
            "Why are you doing this?",
            "Please hurry up!"
        ],
        assigned_to=devops_user.principal_name,
        depends_on=[devops_user]
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


def update_ftp_fqdn() -> dict:
    fqdn = f"{IMAGE_NAME1}{DNS_LABEL}.{LOCATION}.azurecontainer.io"
    files_to_update = [
        "ftpserver/vsftpd.conf",
        "ftppoller/Dockerfile"
    ]
    file_contents = {}

    for file in files_to_update:
        with open(CONTAINER_PATH + file, "r") as f:
            contents = f.read()
            file_contents[file] = contents
            contents = contents.replace(r"{{FQDN}}", fqdn)

        with open(CONTAINER_PATH + file, "w") as f:
            f.write(contents)

    return file_contents

def revert_file_content(file_contents: dict):
    for file, contents in file_contents.items():
        with open(CONTAINER_PATH + file, "w") as f:
            f.write(contents)

def update_flag_file():
    with open(f"{CONTAINER_PATH}/{IMAGE_NAME2}/flag.txt", "w") as f:
        f.write(FLAG)