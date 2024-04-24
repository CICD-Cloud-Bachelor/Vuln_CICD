import pulumi_azure as azure
from source.create_azure_devops import CreateAzureDevops
from source.config import ORGANIZATION_NAME


PROJECT_NAME = "VULN1"
PROJECT_DESCRIPTION = "Project for VULN1"
GITHUB_REPO_URL = "https://github.com/CICD-Cloud-Bachelor/VULN1.git"
REPO_NAME = "VULN1_REPO"
PIPELINE_NAME = "BUILD_PIPELINE"

CHALLENGE_DESCRIPTION = """
This challenge contains a repository and a pipeline that builds the code in the repository. The pipeline has a secret flag that is used during the build process. Your task is to retrieve the flag.
"""
CHALLENGE_CATEGORY = "Easy"
FLAG = "FLAG{you_were_not_supposed_to_find_this}"

def start(
        resource_group: azure.core.ResourceGroup, 
        user: dict
    ):
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
            "FLAG": FLAG
        },
        branch="main",
        run=True
    ) 

    devops_user = CreateAzureDevops.add_entra_user_to_devops(user)
    
    # azure_devops.create_wiki(
    #     wiki_name="VULN1_WIKI"
    # )
    # azure_devops.create_wiki_page(
    #     wiki_name="VULN1_WIKI",
    #     page_name="VULN1_CHALLENGE",
    #     markdown_file_path="vulnerabilities/vuln1/README.md"
    # )