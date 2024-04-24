import pulumi_azure as azure
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
Dette er femte challenge jippi!!
Den er veldig morro og du kommer til å like den
Denne er veldig enkel
"""
FLAG = "FLAG{pwned_the_customer}"

def start(
        resource_group: azure.core.ResourceGroup,
        user: dict
    ):
    update_flag_file()
    original_file_contents = update_ftp_fqdn()

    acr = DockerACR(
        resource_group=resource_group, 
    )

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

    CreateAzureDevops.add_entra_user_to_devops(user)
    azure_devops.create_work_item(
        type="Task",
        title="Deploy FTP Server",
        description="Deploy the FTP server to the Azure Container Registry",
        comments=[
            "Why are you doing this?",
            "Please hurry up!"
        ],
        assigned_to=user["entra_user"].user_principal_name
    )
    
    # azure_devops.create_wiki(
    #     wiki_name="FTP"
    # )
    # azure_devops.create_wiki_page(
    #     wiki_name="FTP",
    #     page_name="FTP Server",
    #     markdown_file_path="vulnerabilities/vuln5/fake_wiki/wiki.md"
    # )







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