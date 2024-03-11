import pulumi_azure as azure
from source.create_azure_devops import CreateAzureDevops
from source.container import DockerACR
from source.workitem import WorkItem
import configparser

config = configparser.ConfigParser()
config.read('config.ini')
REGISTRY_NAME = config["DOCKER"]["REGISTRY_NAME"]
ORGANIZATION_NAME = config["AZURE"]["ORGANIZATION_NAME"]

PROJECT_NAME = "VULN5"
PROJECT_DESCRIPTION = "Project for VULN5"
GITHUB_REPO_URL = "https://github.com/CICD-Cloud-Bachelor/VULN5.git"
REPO_NAME = "VULN5_REPO"
PIPELINE_NAME = "testpipeline"
IMAGE_NAME1 = "ftpserver"
IMAGE_NAME2 = "ftppoller"
CONTAINER_NAME1 = "ftpserver-container"
CONTAINER_NAME2 = "ftppoller-container"

def start(resource_group: azure.core.ResourceGroup):
    # acr = DockerACR(
    #     resource_group=resource_group, 
    #     registry_name=REGISTRY_NAME
    # )
    # acr_string = acr.build_and_push_docker_image(
    #     image_name=IMAGE_NAME1
    # )
    # connection_string = acr.start_container(
    #     docker_acr_image_name=acr_string, 
    #     container_name=CONTAINER_NAME1, 
    #     ports=[21,10000], 
    #     cpu=1.0, 
    #     memory=1.0
    # )
    # acr_string = acr.build_and_push_docker_image(
    #     image_name=IMAGE_NAME2
    # )
    # acr.start_container(
    #     docker_acr_image_name=acr_string, 
    #     container_name=CONTAINER_NAME2, 
    #     ports=[21,10000], 
    #     cpu=1.0, 
    #     memory=1.0
    # )
    
    azure_devops = CreateAzureDevops(
        project_name=PROJECT_NAME, 
        description=PROJECT_DESCRIPTION, 
        organization_name=ORGANIZATION_NAME, 
        resource_group=resource_group
    )
    azure_devops.import_github_repo(
        github_repo_url=GITHUB_REPO_URL, 
        repo_name=REPO_NAME
    )


    azure_devops.create_pipeline(
        name=PIPELINE_NAME,
        variables={
            "FTP_HOST": "a2",#connection_string, 
            "FTP_USER": "ftpshared", 
            "FTP_PASS": "MAsds8ASDsadm82988"
        },
        branch="main",
        run=True
    )


    
