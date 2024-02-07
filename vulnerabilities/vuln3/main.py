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
    ad_user = userCreator.create_user("Tom_Tomington", "Troll57Hoho69%MerryChristmas")

    devops_user = azuredevops.User("Tom",
                                   principal_name = ad_user.user_principal_name
                                   )

    # Get existing Readers group
    readers_group = azuredevops.get_group_output(name = "Readers",
        project_id = adoEnv.project.id
        )

    # Add the user to the group
    azuredevops.GroupMembership("devOpsGroupMembership",
        group = readers_group.descriptor,
        members = [devops_user.descriptor]
        )
    
    pulumi.export('azureDevOpsGroupIdExport', readers_group.id)
    pulumi.export('devopsUserId', devops_user.id)


    