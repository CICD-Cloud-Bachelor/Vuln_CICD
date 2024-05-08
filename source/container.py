import pulumi
import pulumi_azure as azure
import pulumi_azure_native as azure_native
from pulumi_azure_native import containerinstance
import requests, os
import tarfile
from source.config import *

index = 0

class DockerACR:
    """
    DockerACR class represents a Docker Azure Container Registry. 
    """

    IMAGE_TAG = "v1.0"

    def __init__(
            self, 
            resource_group: azure.core.ResourceGroup, 
        ) -> None:
        """
        Initializes a new instance of the Docker Azure Container Registry class.

        Args:
            resource_group (pulumi.ResourceGroup): The resource group where the registry will be created.
            registry_name (str): The name of the registry.

        """
        global index
        index += 1
        self.resource_group = resource_group
        self.registry_name = REGISTRY_NAME
        self.__create_registry()
        self.__create_storage_account_and_container()

    def __create_registry(self) -> None:
        """
        Creates an Azure Container Registry in the specified resource group with basic configuration.

        This method is called internally during initialization.
        """
        pulumi.log.info(f"Creating registry: {self.registry_name}")
        self.registry = azure_native.containerregistry.Registry(
            resource_name=self.registry_name,
            resource_group_name=self.resource_group.name,
            sku=azure_native.containerregistry.SkuArgs(
                name="Basic"
            ),
            location=self.resource_group.location,
            admin_user_enabled=True,
        )

        # Obtain registry credentials for Docker
        self.credentials = azure_native.containerregistry.list_registry_credentials_output(
            resource_group_name=self.resource_group.name,
            registry_name=self.registry.name,
        )

    def __get_public_ip(self) -> str:
        return requests.get('https://api64.ipify.org').text
    
    def __create_storage_account_and_container(self) -> None:
        """
        Sets up a storage account and container for handling Docker image files. This is used for storing Docker images as blobs.

        This method is called internally during initialization.
        """
        self.storage_account = azure.storage.Account(
            resource_name=f"storAcc{os.urandom(7).hex()}",
            name=STORAGE_ACCOUNT_NAME + str(index),
            resource_group_name=self.resource_group.name,
            location=self.resource_group.location,
            account_tier="Standard",
            account_replication_type="LRS"
        )
        self.storage_container = azure.storage.Container(
            resource_name=f"storCont{os.urandom(7).hex()}",
            name=STORAGE_CONTAINER_NAME + str(index),
            storage_account_name=self.storage_account.name,
            container_access_type="container",
            opts=pulumi.ResourceOptions(depends_on=[self.storage_account])
        )

    def __upload_file_to_blob(self, image_name: str) -> None:
        """
        Uploads a Docker image file to Azure Blob Storage after creating a tar archive of the image.

        Args:
            image_name (str): The name of the Docker image to be uploaded.

        Example:
            >>> self.__upload_file_to_blob('example_image')
        """
        self.__create_tar_archive(
            image_name=image_name
        )
        self.blob_storage = azure.storage.Blob(
            resource_name=f"blobStor{os.urandom(7).hex()}",
            name=f"{image_name}.tar", # the filename
            storage_account_name=self.storage_account.name,
            storage_container_name=self.storage_container.name,
            type="Block",
            source=pulumi.FileAsset(f"{CONTAINER_PATH}/.tarfiles/{image_name}.tar"),
            opts=pulumi.ResourceOptions(depends_on=[self.storage_container, self.storage_account])
        )
        
    
    def __build_and_push_docker_image(
        self, 
        image_name: str #image name needs to be same as the folder name, no underscores or special chars
        ) -> str:
        """
        Builds and pushes a Docker image to the configured Azure Container Registry.

        Args:
            image_name (str): The name of the Docker image.

        Returns:
            str: The repository path of the Docker image in the registry.

        Example:
            >>> self.__build_and_push_docker_image('example_image')
        """
        pulumi.log.info(f"Running Docker Compose for image: {image_name}")

        self.task = azure_native.containerregistry.TaskRun(f"taskRun{image_name}",
            force_update_tag="test",
            location=self.resource_group.location,
            registry_name=self.registry.name,
            resource_group_name=self.resource_group.name,
            run_request=azure_native.containerregistry.DockerBuildRequestArgs(
                source_location=f"https://{STORAGE_ACCOUNT_NAME}{index}.blob.core.windows.net/{STORAGE_CONTAINER_NAME}{index}/{image_name}.tar",
                docker_file_path="Dockerfile",
                image_names=[f"image/{image_name}:{self.IMAGE_TAG}"],
                is_push_enabled=True,
                is_archive_enabled=True,
                no_cache=False,
                type="Docker",
                platform=azure_native.containerregistry.PlatformPropertiesArgs(
                    os="Linux",
                ),
            ),
            task_run_name=f"myRunCompose{image_name}",
            opts=pulumi.ResourceOptions(depends_on=[self.blob_storage])
        )
        #print(f"TASK {index}: https://{STORAGE_ACCOUNT_NAME}{index}.blob.core.windows.net/{STORAGE_CONTAINER_NAME}{index}/{image_name}.tar")

        return self.registry.login_server.apply(lambda login_server: f"{login_server}/image/{image_name}:{self.IMAGE_TAG}")

    def __create_tar_archive(
        self,
        image_name: str
        ) -> None:
        """
        Creates a tar archive of the specified Docker image directory for uploading.

        Args:
            image_name (str): The name of the Docker image.

        Example:
            >>> self.__create_tar_archive('example_image')
        """
        pulumi.log.info(f"Creating {CONTAINER_PATH}/.tarfiles/{image_name}.tar")
        with tarfile.open(f"{CONTAINER_PATH}/.tarfiles/{image_name}.tar", "w") as tar:
            for name in os.listdir(f"{CONTAINER_PATH}/{image_name}"):
                pulumi.log.info(f"Adding {name} to archive")
                tar.add(f"{CONTAINER_PATH}/{image_name}/{name}", arcname=name)
    
    def __remove_tar_archive(
            self, 
            image_name: str
        ) -> None:
        """
        Removes the tar archive of a Docker image after it has been uploaded to Azure Blob Storage.

        Args:
            image_name (str): The name of the Docker image whose tar file is to be removed.

        Example:
            >>> self.__remove_tar_archive('example_image')
        """
        pulumi.log.info(f"Removing {CONTAINER_PATH}/.tarfiles/{image_name}.tar")
        for file in os.listdir(f"{CONTAINER_PATH}/.tarfiles/"):
            pulumi.log.info(f"Removing {file}")
            if file.endswith(".tar"):
                os.remove(f"{CONTAINER_PATH}/.tarfiles/{file}")

    def start_container(
                self, 
                image_name: str, # must be the name of a folder in the "CONTAINER_PATH" folder
                ports: list[int], 
                cpu: float, 
                memory: float
            ) -> pulumi.Output[any]:
            """
            Starts a Docker container from an image stored in Azure Container Registry with specified configurations.
    
            Args:
                image_name (str): The name of the Docker image.
                ports (list[int]): A list of ports to expose from the container.
                cpu (float): The amount of CPU to allocate to the container.
                memory (float): The amount of memory (in GB) to allocate to the container.
    
            Returns:
                str: The fully qualified domain name (FQDN) of the container.
    
            Example:
                >>> docker_acr.start_container('example_image', [80, 443], 1.0, 1.5)
            """
            self.__upload_file_to_blob(
                image_name=image_name
            )

            docker_acr_image_name = self.__build_and_push_docker_image(
                image_name=image_name
            )

            pulumi.log.info(f"Starting container: {image_name}")
            
            container_group = containerinstance.ContainerGroup(
                resource_name=f"cgroup-{image_name}-{os.urandom(5).hex()}",
                resource_group_name=self.resource_group.name,
                os_type="Linux",  # or "Windows"
                containers=[
                    containerinstance.ContainerArgs(
                        name=image_name,
                        image=docker_acr_image_name,
                        resources=containerinstance.ResourceRequirementsArgs(
                            requests=containerinstance.ResourceRequestsArgs(
                                cpu=cpu,
                                memory_in_gb=memory,
                            ),
                        ),
                        ports=[containerinstance.ContainerPortArgs(port=p) for p in ports],
                    ),
                ],
                image_registry_credentials=[
                    containerinstance.ImageRegistryCredentialArgs(
                        server=self.registry.login_server.apply(lambda server: server),
                        username=self.credentials.apply(lambda creds: creds.username),
                        password=self.credentials.apply(lambda creds: creds.passwords[0].value),
                    ),
                ],
                ip_address=containerinstance.IpAddressArgs(
                    ports=[
                        containerinstance.PortArgs(
                            protocol="TCP", 
                            port=p
                            ) for p in ports
                    ],
                    type="Public",
                    dns_name_label=f"{image_name}{DNS_LABEL}",
                ),
                restart_policy="OnFailure",
                opts=pulumi.ResourceOptions(depends_on=[self.task])
            )
            # Construct the FQDN
            fqdn = pulumi.Output.all(
                container_group.name, 
                container_group.location
            ).apply(
                lambda args: f"{image_name}{DNS_LABEL}.{args[1]}.azurecontainer.io"
            )
            return fqdn