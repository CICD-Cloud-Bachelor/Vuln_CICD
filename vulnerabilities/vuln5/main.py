import pulumi_azure as azure
from source.create_azure_devops import CreateAzureDevops
from source.container import DockerACR
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
CONTAINER_NAME1 = "ftp-container"
CONTAINER_NAME2 = "ftppoller-container"

def start(resource_group: azure.core.ResourceGroup):
    acr = DockerACR(resource_group, REGISTRY_NAME)
    
    acr_string = acr.build_and_push_docker_image(IMAGE_NAME1)
    connection_string = acr.start_container(
        docker_acr_image_name=acr_string, 
        container_name=CONTAINER_NAME1, 
        ports=[21,10000], 
        cpu=1.0, 
        memory=1.0
    )

    acr_string = acr.build_and_push_docker_image(IMAGE_NAME2)
    acr.start_container(
        docker_acr_image_name=acr_string, 
        container_name=CONTAINER_NAME2, 
        ports=[21,10000], 
        cpu=1.0, 
        memory=1.0
    )
    
    azure_devops = CreateAzureDevops(
        PROJECT_NAME, 
        PROJECT_DESCRIPTION, 
        ORGANIZATION_NAME, 
        resource_group
    )

    azure_devops.import_github_repo(GITHUB_REPO_URL, REPO_NAME)
    
    azure_devops.add_variables(
        {
            "FTP_HOST": connection_string, 
            "FTP_USER": "ftpshared", 
            "FTP_PASS": "MAsds8ASDsadm82988"
        }
    )
    
    azure_devops.create_ci_cd_pipeline(PIPELINE_NAME)
