import pulumi_azure as azure
from source.create_azure_devops import CreateAzureDevops
import configparser

config = configparser.ConfigParser()
config.read('config.ini')
ORGANIZATION_NAME = config["AZURE"]["ORGANIZATION_NAME"]
FLAG = config["FLAGS"]["VULN1"]

PROJECT_NAME = "VULN1"
PROJECT_DESCRIPTION = "Project for VULN1"
GITHUB_REPO_URL = "https://github.com/CICD-Cloud-Bachelor/VULN1.git"
REPO_NAME = "VULN1_REPO"
PIPELINE_NAME = "BUILD_PIPELINE"

def start(resource_group: azure.core.ResourceGroup):
    azure_devops = CreateAzureDevops(
        project_name=PROJECT_NAME, 
        description=PROJECT_DESCRIPTION, 
        organization_name=ORGANIZATION_NAME,
        resource_group=resource_group
    )

    azure_devops.import_github_repo(GITHUB_REPO_URL, REPO_NAME)

    
    azure_devops.add_variables( # implementere denne inni create_ci_cd_pipeline
        {
            "FLAG": FLAG
        }
    )
    azure_devops.create_ci_cd_pipeline(PIPELINE_NAME) # bytte navn på denne
    azure_devops.run_pipeline(branch="main")
