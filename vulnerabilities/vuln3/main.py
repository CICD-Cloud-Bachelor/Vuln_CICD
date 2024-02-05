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

    userCreator = CreateUsers("mohammedhussaini1268gmail.onmicrosoft.com")
    ad_user = userCreator.create_user("Troll_Trollington", "Troll57Hoho69%MerryChristmas")

    devops_user = azuredevops.User("Troll",
                                   principal_name = ad_user.user_principal_name
                                   )
    

    # Create an Azure DevOps Group at the project level
    devops_group = azuredevops.Group("devOpsGroup",
        scope = adoEnv.project.id, # Scope the group to the project level
        display_name="PulumiManagedDevOpsGroup",
        members = [
            devops_user.descriptor
        ]
        )


    # Export the IDs of the created groups
    pulumi.export('azureDevOpsGroupIdExport', devops_group.id)


    