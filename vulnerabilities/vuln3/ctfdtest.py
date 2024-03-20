import time
import pulumi
import pulumi_azure as azure
import pulumi_azure_native as azure_native
import pulumi_azuread as azuread
import configparser
import pulumi_synced_folder
from pulumi_command import local
from source.container import DockerACR

config = configparser.ConfigParser()
config.read('config.ini')
ORGANIZATION_NAME = config["AZURE"]["ORGANIZATION_NAME"]
STORAGE_ACCOUNT_NAME = "ystorgeacnt5419"
BLOB_CONTAINER_NAME = "myblobcontainer"

def start(resource_group: azure.core.ResourceGroup):
    # Create an Azure Container Registry
    acr = azure_native.containerregistry.Registry('pulumiregistry',
        resource_group_name=resource_group.name.apply(lambda name: f"{name}"),
        location="West Europe",
        sku=azure_native.containerregistry.SkuArgs(name='Basic'),
        admin_user_enabled=True
    )

    # Create a Blob Storage Account
    storage_account = azure_native.storage.StorageAccount(STORAGE_ACCOUNT_NAME,
        location="West Europe",
        resource_group_name=resource_group.name.apply(lambda name: f"{name}"),
        sku=azure_native.storage.SkuArgs(name='Standard_LRS'),
        kind='StorageV2',
        allow_blob_public_access=True
    )

    
    # Create a Blob Container within the storage account
    blob_container = azure_native.storage.BlobContainer(BLOB_CONTAINER_NAME,
        account_name=storage_account.name.apply(lambda name: f"{name}"),
        resource_group_name=resource_group.name.apply(lambda name: f"{name}"),
        public_access='Blob'
    )

    # Upload folder to blob
    folder = pulumi_synced_folder.AzureBlobFolder("CTFd", pulumi_synced_folder.AzureBlobFolderArgs(
        resource_group_name=resource_group.name.apply(lambda name: f"{name}"),
        storage_account_name=storage_account.name.apply(lambda name: f"{name}"),
        container_name=blob_container.name.apply(lambda name: f"{name}"),
        path="../CTFd",
        )
    )

    # Define and run an ACR task to build the Docker image
    # acr_task = azure_native.containerregistry.Task('my-acr-task',
    #     task_name='docker-build-task',
    #     resource_group_name=resource_group.name.apply(lambda name: f"{name}"),
    #     registry_name=acr.name,
    #     location="West Europe",
    #     agent_configuration=azure_native.containerregistry.AgentPropertiesArgs(
    #         cpu=2
    #     ),
    #     platform=azure_native.containerregistry.PlatformPropertiesArgs(
    #         os='Linux',
    #         architecture='amd64'
    #     ),
    #     step=azure_native.containerregistry.DockerBuildStepArgs(
    #         context_path=f'https://{storage_account.name.apply(lambda name: f"{name}")}.blob.core.windows.net/{blob_container.name.apply(lambda name: f"{name}")}',
    #         image_names=['CTFd:latest'],
    #         docker_file_path='Dockerfile',
    #         type='Docker'
    #     ),
    #     # Use identity-based authentication for the task runner
    #     identity=azure_native.containerregistry.IdentityPropertiesArgs(
    #         type='SystemAssigned'
    #     ),
    #     trigger=azure_native.containerregistry.TriggerPropertiesArgs(
    #         source_triggers=[
    #             azure_native.containerregistry.SourceTriggerArgs(
    #                 name='defaultSourceTrigger',
    #                 source_repository=azure_native.containerregistry.SourcePropertiesArgs(
    #                     source_control_type='None',
    #                     repository_url=f'https://{storage_account.name.apply(lambda name: f"{name}")}.blob.core.windows.net/{blob_container.name.apply(lambda name: f"{name}")}',
    #                 ),
    #                 source_trigger_events=['commit'],
    #                 status='Enabled'
    #             )
    #         ]
    #     )
    # )

    # Export the ACR login server and the storage account endpoint
    pulumi.export('acr_server', acr.login_server)
    pulumi.export('storage_account_endpoint', storage_account.primary_endpoints.apply(lambda endpoints: endpoints.blob))

