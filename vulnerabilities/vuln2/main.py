import pulumi
import pulumi_azure as azure
import markovify
from source.create_azure_devops import CreateAzureDevops

def start(resource_group: azure.core.ResourceGroup):
    azure_devops = CreateAzureDevops("vul2_test", "Test for å lage wiki", "bachelor2024", resource_group)
    azure_devops.create_work_item(10)
    azure_devops.create_work_item(
            count=1,
            work_item_type="Epic",
            work_item_title="Mo må fikse permissions",
            work_item_state="New",
            work_item_description="Password for the new user will be sent to the email address provided."
        )

    azure_devops.add_comment_to_work_item(885, "Dette er en kommentar")

    
