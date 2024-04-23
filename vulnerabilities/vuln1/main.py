import pulumi_azure as azure
from source.create_azure_devops import CreateAzureDevops
from source.config import ORGANIZATION_NAME, FLAGS


PROJECT_NAME = "VULN1"
PROJECT_DESCRIPTION = "Project for VULN1"
GITHUB_REPO_URL = "https://github.com/CICD-Cloud-Bachelor/VULN1.git"
REPO_NAME = "VULN1_REPO"
PIPELINE_NAME = "BUILD_PIPELINE"

CHALLENGE_DESCRIPTION = """
Dette er første challenge jippi!!
Den er veldig morro og du kommer til å like den
Denne er veldig enkel
"""
CHALLENGE_CATEGORY = "Easy"
FLAG = "FLAG{flag1}"

def start(resource_group: azure.core.ResourceGroup):
    azure_devops = CreateAzureDevops(
        project_name=PROJECT_NAME, 
        description=PROJECT_DESCRIPTION, 
        organization_name=ORGANIZATION_NAME,
        resource_group=resource_group
    )

    azure_devops.import_github_repo(GITHUB_REPO_URL, REPO_NAME)

    azure_devops.create_pipeline(
        name=PIPELINE_NAME,
        variables={
            "FLAG": FLAGS["vuln1"]
        },
        branch="main",
        run=True
    ) 
    
