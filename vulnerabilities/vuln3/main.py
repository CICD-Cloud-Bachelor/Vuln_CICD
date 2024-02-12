import pulumi
import pulumi_azure as azure
import pulumi_azuread as azuread
import pulumi_azuredevops as azuredevops
from source.users_groups import UserCreator, GroupCreator
from source.create_azure_devops import CreateAzureDevops
from source.container import CreateContainer



def start():
    resource_group = azure.core.ResourceGroup('resource-group', location="West Europe")

    github_repo_url = "https://github.com/flis5/svakhet3.git"

    create_devops = CreateAzureDevops("Vulnerability 3", "Insufficient Credential Hygiene", "hackegutta", resource_group)
    create_devops.import_github_repo(github_repo_url, "Vulnerabity_3")
    vuln3_pipeline = create_devops.create_ci_cd_pipeline("Vulnerability-3-CICD-Pipeline")

    
    user_creator = UserCreator("mohammedhussaini1268gmail.onmicrosoft.com")
    devops_user = user_creator.create_devops_user("Tom_Tomington", "Troll57Hoho69%MerryChristmas")

    # Add user to Readers group so they can view the project
    GroupCreator.add_user_to_group(devops_user, create_devops.readers_group)
    
    # Allow user to run pipelines
    GroupCreator.modify_pipeline_permissions(create_devops.project, create_devops.readers_group, vuln3_pipeline,
        permissions = {
            "QueueBuilds": "Allow",
        }
    )

    pulumi.export('devopsUserId', devops_user.id)
