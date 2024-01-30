import pulumi_azure as azure
from source.add_users import CreateUsers
from source.create_azure_devops import CreateAzureDevops
from source.container import CreateContainer



def start():
    resource_group = azure.core.ResourceGroup('resource-group', location="West Europe")

    github_repo_url = "https://github.com/flis5/svakhet3.git"

    azure_devops = CreateAzureDevops("Vulnerability 3", "Insufficient Credential Hygiene", "bachelor2024", resource_group)
    azure_devops.import_github_repo(github_repo_url, "Vulnerabity_3")