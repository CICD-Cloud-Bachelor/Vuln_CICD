import pulumi_azure as azure
from source.create_azure_devops import CreateAzureDevops
from source.container import DockerACR
from source.workitem import WorkItem
import configparser

config = configparser.ConfigParser()
config.read('config.ini')
ORGANIZATION_NAME = config["AZURE"]["ORGANIZATION_NAME"]
REGISTRY_NAME = config["DOCKER"]["REGISTRY_NAME"]

PROJECT_NAME = "VULN4"
PROJECT_DESCRIPTION = "Project for VULN4"
GITHUB_REPO_URL = "https://github.com/CICD-Cloud-Bachelor/VULN4.git"
REPO_NAME = "VULN4_REPO"
PIPELINE_NAME = "testpipeline"
IMAGE_NAME = "mysqldb"
CONTAINER_NAME = "mysql-container"

def start(resource_group: azure.core.ResourceGroup):
    acr = DockerACR(
        resource_group=resource_group, 
        registry_name=REGISTRY_NAME
    )
    
    acr_string = acr.build_and_push_docker_image(
        image_name=IMAGE_NAME
    )

    connection_string = acr.start_container(
        docker_acr_image_name=acr_string, 
        container_name=CONTAINER_NAME, 
        ports=[3306], 
        cpu=1.0, 
        memory=1.0
    )
    
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
    
    azure_devops.add_variables(
        {
            "CONNECTION_STRING": connection_string, 
            "DATABASE": "prod", 
            "USERNAME": "root", 
            "PASSWORD": "myr00tp455w0rd"
        }
    )
    
    azure_devops.create_ci_cd_pipeline(
        name=PIPELINE_NAME
    )
    
    workitem = WorkItem(
        organization_name=ORGANIZATION_NAME, 
        project_name=PROJECT_NAME, 
        depends_on=azure_devops.project
    )
    
    workitem.create(
        type="Task", 
        title="Magnus Magnusen", 
        description="yoooooooooooooooooooooooo", 
        comment="kommentarhei"
    )
    workitem.create(
        type="Epic", 
        title="Mo Moesen", 
        description="heihei", 
        comment="kommentarsandkasndkajs"
    )
    
    workitem.create_random_work_items(10)