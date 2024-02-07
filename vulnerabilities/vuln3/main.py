import pulumi
import pulumi_azure as azure
import pulumi_azuread as azuread
import pulumi_azuredevops as azuredevops
from source.add_users import CreateUsers
from source.create_azure_devops import CreateAzureDevops
from source.container import CreateContainer



def start():
    resource_group = azure.core.ResourceGroup('resource-group', location="West Europe")

    github_repo_url = "https://github.com/flis5/svakhet3.git"

    adoEnv = CreateAzureDevops("Vulnerability 3", "Insufficient Credential Hygiene", "hackegutta", resource_group)
    adoEnv.import_github_repo(github_repo_url, "Vulnerabity_3")
    adoEnv.create_ci_cd_pipeline("Vulnerability-3-CICD-Pipeline")

    userCreator = CreateUsers("mohammedhussaini1268gmail.onmicrosoft.com")
    devops_user = userCreator.create_devops_user("Tom_Tomington", "Troll57Hoho69%MerryChristmas")

    # Add user to Readers group so they can view the project
    adoEnv.add_user_to_group(devops_user, adoEnv.readers_group)
    
    # Allow user to run pipelines
    adoEnv.modify_pipeline_permissions(adoEnv.readers_group,
        permissions = {
            "QueueBuilds": "Allow",
        }
        )

    pulumi.export('devopsUserId', devops_user.id)


    