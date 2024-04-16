import pulumi
import pulumi_azure as azure
import pulumi_docker as docker
import pulumi_azure_native as azure_native
from pulumi_azure_native import containerinstance, resources
from pulumi_azure_native import network, dbformysql
import requests, os
import tarfile
import subprocess
import shutil
import json
import zipfile
import configparser
from source.config import *

index = 0

config = configparser.ConfigParser()
config.read('config.ini')

FLAG1 = config["FLAGS"]["VULN1"]
FLAG2 = config["FLAGS"]["VULN2"]
FLAG3 = config["FLAGS"]["VULN3"]
FLAG4 = config["FLAGS"]["VULN4"]
FLAG5 = config["FLAGS"]["VULN5"]

flags = [FLAG1, FLAG2, FLAG3, FLAG4, FLAG5]

descriptions = [
    "SQL Injection",
    "Cross-Site Scripting (XSS)",
    "Cross-Site Request Forgery (CSRF)",
    "Remote Code Execution (RCE)",
    "Command Injection"
]

class DockerACR:
    """
    DockerACR class represents a Docker Azure Container Registry.

    Args:
        resource_group (pulumi.ResourceGroup): The resource group where the registry will be created.
        registry_name (str): The name of the registry.

    Attributes:
        IMAGE_TAG (str): The tag for the Docker image.

    Methods:
        __init__(self, resource_group, registry_name): Initializes a new instance of the DockerACR class.
        __create_registry(self): Creates the Azure Container Registry.
        build_and_push_docker_image(self, image_name): Builds and pushes a Docker image to the registry.
        start_container(self, image_name, container_name, ports, cpu, memory): Starts a container in a container group.

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
        self.resource_group = resource_group
        self.registry_name = REGISTRY_NAME
        self.__create_registry()
        self.__create_storage_account_and_container()

    def __create_registry(self) -> None:
        """
        Creates the Azure Container Registry.
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
        self.storage_account = azure.storage.Account(
            resource_name=f"storageAccountPulumiBachelor2024{index}",
            name=STORAGE_ACCOUNT_NAME,
            resource_group_name=self.resource_group.name,
            location=self.resource_group.location,
            account_tier="Standard",
            account_replication_type="LRS"
        )
        self.storage_container = azure.storage.Container(
            resource_name=f"storageContainerPulumiBachelor2024{index}",
            name=STORAGE_CONTAINER_NAME,
            storage_account_name=self.storage_account.name,
            container_access_type="container"
        )

    def __upload_file_to_blob(self, image_name: str) -> None:
        global index
        self.__create_tar_archive(
            image_name=image_name
        )
        self.blob_storage = azure.storage.Blob(
            resource_name=f"blobStoragePulumiBachelor2024{index}",
            name=f"{image_name}.tar", # the filename
            storage_account_name=self.storage_account.name,
            storage_container_name=self.storage_container.name,
            type="Block",
            source=pulumi.FileAsset(f"{CONTAINER_PATH}/{image_name}.tar")
        )
        # self.__remove_tar_archive(
        #     image_name=image_name
        # )
        
    
    def __build_and_push_docker_image(
        self, 
        image_name: str #image name needs to be same as the folder name
        ) -> str:
        pulumi.log.info(f"Running Docker Compose for image: {image_name}")

        self.task = azure_native.containerregistry.TaskRun(f"taskRun{image_name}",
            force_update_tag="test",
            location=self.resource_group.location,
            registry_name=self.registry.name,
            resource_group_name=self.resource_group.name,
            run_request=azure_native.containerregistry.DockerBuildRequestArgs(
                source_location=f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net/{STORAGE_CONTAINER_NAME}/{image_name}.tar",
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
        return self.registry.login_server.apply(lambda login_server: f"{login_server}/image/{image_name}:{self.IMAGE_TAG}")

    def __create_tar_archive(
        self,
        image_name: str
        ) -> None:
        pulumi.log.info(f"Creating {CONTAINER_PATH}/{image_name}.tar")
        with tarfile.open(f"{CONTAINER_PATH}/{image_name}.tar", "w") as tar:
            for name in os.listdir(f"{CONTAINER_PATH}/{image_name}"):
                pulumi.log.info(f"Adding {name} to archive")
                tar.add(f"{CONTAINER_PATH}/{image_name}/{name}", arcname=name)
    
    def __remove_tar_archive(
            self, 
            image_name: str
        ) -> None:
        pulumi.log.info(f"Removing {CONTAINER_PATH}/{image_name}.tar")
        for file in os.listdir(CONTAINER_PATH):
            pulumi.log.info(f"Removing {file}")
            if file.endswith(".tar"):
                os.remove(f"{CONTAINER_PATH}/{file}")

    def start_container(
                self, 
                image_name: str, # must be the name of a folder in the "CONTAINER_PATH" folder
                ports: list[int], 
                cpu: float, 
                memory: float
            ) -> str:
            """
            Starts a container with the specified image name, ports, CPU, and memory.

            Args:
                image_name (str): The name of the folder in the "CONTAINER_PATH" folder that contains the image.
                ports (list[int]): A list of port numbers to expose on the container.
                cpu (float): The CPU allocation for the container.
                memory (float): The memory allocation (in GB) for the container.

            Returns:
                str: The fully qualified domain name (FQDN) of the container.

            Raises:
                None

            """
            global index
            self.__upload_file_to_blob(
                image_name=image_name
            )

            docker_acr_image_name = self.__build_and_push_docker_image(
                image_name=image_name
            )

            pulumi.log.info(f"Starting container: {image_name}")
            
            container_group = containerinstance.ContainerGroup(
                resource_name=f"pulumi-containergroup-{image_name}-{index}",
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
            index += 1
            return fqdn

class CtfdContainer:
    """
    Represents a CTFd container.

    This class provides methods to manage a CTFd container, including initializing the container,
    running docker-compose commands, and replacing challenge flags and descriptions.

    Attributes:
        ctfd_export_path (str): The path to the CTFd export zip file.
        ctfd_path (str): The path to the CTFd directory.
    """

    #####
    # A heads up - The code assumes the ctfd_export template has the challenges set up with placeholder flags.
    # This is so that the flags json file has an entry for the respective challenges.
    # The default ctfd_export.zip has 5 challenges configured, with their id being 1-5 respectively.
    #####

    def __init__(self):
        """
        Initializes a new instance of the CtfdContainer class.

        This method sets the ctfd_path attribute and replaces challenge flags and descriptions
        in the CTFd export zip file. It then runs the docker-compose command to start the container.
        """
        self.ctfd_path = f"{CONTAINER_PATH}/CTFd"
        self.__replace_chall_flags_and_descriptions(self.ctfd_path)
        self.__run_docker_compose(['--project-directory', self.ctfd_path, 'up', '-d'])

    def __run_docker_compose(self, command: list[str]):
        """
        Runs a docker-compose command and prints its output.

        :param command: List of the command parts, e.g., ['up', '-d'] for 'docker-compose up -d'.
        """
        # Ensure the command is prefixed with 'docker-compose'
        docker_compose_cmd = ['docker-compose'] + command

        # Run the command
        process = subprocess.Popen(docker_compose_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for the command to complete
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            print("Docker compose executed successfully")
            print(stdout.decode())
        else:
            print("Error executing docker compose")
            print(stderr.decode())

    def __unzip_file(self, zip_file: str, extraction_dir: str) -> None:
        """
        Extracts a zip file to the specified directory.

        :param zip_file: The path to the zip file.
        :param extraction_dir: The directory to extract the files to.
        """
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(extraction_dir)

    def __zip_dir(self, dir: str, zip_file: str) -> None:
        """
        Zips a directory and its contents.

        :param dir: The path to the directory.
        :param zip_file: The path to the zip file to create.
        """
        shutil.make_archive(zip_file, 'zip', dir)

    def __delete_dir(self, dir: str) -> None:
        """
        Deletes a directory and its contents.

        :param dir: The path to the directory.
        """
        shutil.rmtree(dir)

    def __read_json(self, file: str) -> dict:
        """
        Reads a JSON file and returns its contents as a dictionary.

        :param file: The path to the JSON file.
        :return: The contents of the JSON file as a dictionary.
        """
        with open(file, 'r') as f:
            data = json.load(f)
        return data

    def __write_json(self, file: str, data: dict) -> None:
        """
        Writes a dictionary to a JSON file.

        :param file: The path to the JSON file.
        :param data: The dictionary to write to the file.
        """
        with open(file, 'w') as f:
            json.dump(data, f)

    def __replace_flags(self, flag_dict: dict, flags: list) -> None:              
        """
        Replaces the flags in the flag dictionary with the provided flags.

        :param flag_dict: The flag dictionary.
        :param flags: The list of flags to replace the existing flags with.
        """
        for flag_entry in flag_dict["results"]:
            index = flag_entry["id"] - 1
            flag = flags[index]
            flag_entry["content"] = flag
        return flag_dict

    def __replace_descriptions(self, chall_dict: dict, descriptions: list) -> None:
        """
        Replaces the descriptions in the challenge dictionary with the provided descriptions.

        :param chall_dict: The challenge dictionary.
        :param descriptions: The list of descriptions to replace the existing descriptions with.
        """
        for chall_entry in chall_dict["results"]:
            index = chall_entry["id"] - 1
            description = descriptions[index]
            chall_entry["description"] = description
        return chall_dict
    
    def __replace_chall_flags_and_descriptions(self, ctfd_path: str):
        """
        Replaces the challenge flags and descriptions in the CTFd export zip file.

        :param ctfd_export_path: The path to the CTFd export zip file.
        """
        pulumi.log.info("Replacing challenge flags and descriptions in CTFd export")
        temp_dir = "ctfd_export_temp_dir/"
        db_path = "ctfd_export_temp_dir/db/"

        ctfd_export_path = ctfd_path + "/ctfd_export.zip"
        self.__unzip_file(ctfd_export_path, temp_dir)

        old_flags = self.__read_json(db_path + "flags.json")
        old_challs = self.__read_json(db_path + "challenges.json")

        new_flags_dict = self.__replace_flags(old_flags, flags)
        new_challs_dict = self.__replace_descriptions(old_challs, descriptions)

        self.__write_json(db_path + "flags.json", new_flags_dict)
        self.__write_json(db_path + "challenges.json", new_challs_dict)

        self.__zip_dir(temp_dir, ctfd_path + "/ctfd_export") # shutil adds .zip to the filename
        self.__delete_dir(temp_dir)