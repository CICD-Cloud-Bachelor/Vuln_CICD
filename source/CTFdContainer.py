import pulumi
import zipfile
import shutil
import json
import importlib
import os
from source.container import DockerACR
from source.config import *

class CTFdContainer:
    """
    Manages a CTFd (Capture The Flag daemon) container setup, including customizing flags, descriptions,
    and running the container using Azure Container Instances.
    """
    
    def __init__(self, username: str, password: str, acr: DockerACR):
        """
        Initializes a new instance of the CtfdContainer class.

        This method sets the ctfd_path attribute and replaces challenge flags and descriptions
        in the CTFd export zip file. It then runs the start_container method from container.py to upload it to Azure.

        Args:
            username (str): The username for the Azure DevOps user.
            password (str): The password for the Azure DevOps user.
        """
        self.flags_db = {
            "count": 0,
            "results": [],
            "meta": {}
        }
        self.challenges_db = {
            "count": 0,
            "results": [],
            "meta": {}
        }
        self.acr = acr
        self.descriptions = {}
        self.categories = {}
        self.flags = {}
        self.login_name = f"{username.replace(' ', '.')}@{DOMAIN}"
        self.entra_password = password
        self.ctfd_path = f"{CONTAINER_PATH}/ctfd"
        self.organization_link = f"https://dev.azure.com/{ORGANIZATION_NAME}"
        self.__replace_ctfd_export_flags_and_descriptions()

        ctfd_link = self.acr.start_container(
            image_name="ctfd", 
            ports=[8000], 
            cpu=1.0,
            memory=1.0
        )
        pulumi.export("CTFd Link", ctfd_link)
        pulumi.export("CTFd port", "8000")
        pulumi.export("CTFd login", "hacker")
        pulumi.export("CTFd password", "hacker")

    def __unzip_file(self, zip_file: str, extraction_dir: str) -> None:
        """
        Creates a zip file from the specified directory.

        Args:
            zip_file (str): The path to the zip file to create.
            extraction_dir (str): The path to the directory to zip.

        Example:
            >>> self.__unzip_dir('path/to/directory', 'path/to/file.zip')
        """
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(extraction_dir)

    def __zip_dir(self, dir: str, zip_file: str) -> None:
        """
        Creates a zip file from the specified directory.

        Args:
            dir (str): The path to the directory to zip.
            zip_file (str): The path to the zip file to create.

        Example:
            >>> self.__zip_dir('path/to/directory', 'path/to/file.zip')
        """
        shutil.make_archive(zip_file, 'zip', dir)

    def __delete_dir(self, dir: str) -> None:
        """
        Deletes a directory and its contents.

        Args:
            dir (str): The path to the directory to delete.

        Example:
            >>> self.__delete_dir('path/to/directory')
        """
        shutil.rmtree(dir)

    def __write_json(self, file: str, data: dict) -> None:
        """
        Writes a dictionary to a JSON file.

        Args:
            file (str): The file path to write the JSON data to.
            data (dict): The dictionary data to write.
        
        Example:
            >>> self.__write_json('path/to/file.json', {'key': 'value'})
        """
        with open(file, 'w') as f:
            json.dump(data, f)
    
    def __get_vuln_descriptions_and_categories_and_flags(self) -> None:
        """
        Retrieves vulnerability descriptions, categories, and flags for each vulnerability module and stores them in dictionaries.

        This method dynamically imports each vulnerability module and extracts required information.

        Example:
            >>> self.__get_vuln_descriptions_and_categories_and_flags()
        """
        description_login_info = f'\n\nLogin: {self.login_name}\n\nPassword: {self.entra_password}\n\n<a href={self.organization_link}>{self.organization_link}</a>'
        
        vuln_folders = [folder for folder in os.listdir('vulnerabilities/') if folder.startswith('vuln')]
        number_of_vulns = len(vuln_folders)

        vuln_modules = []
        for i in range(number_of_vulns):
            vuln_modules.append(f"vulnerabilities.vuln{i+1}.main")

        for vuln_name in vuln_modules:
            vuln = importlib.import_module(vuln_name)
            vuln_key = vuln.__name__.replace("vulnerabilities.", "").replace(".main", "")
            self.descriptions[vuln_key] = vuln.CHALLENGE_DESCRIPTION + description_login_info
            self.categories[vuln_key] = vuln.CHALLENGE_CATEGORY
            self.flags[vuln_key] = vuln.FLAG
    
    def __fill_flags_db_and_challenges_db(self) -> None:
        """
        Fills the flags and challenges databases with the necessary data.

        This method retrieves vulnerability descriptions, categories, and flags,
        and populates the challenges and flags databases accordingly. It assigns
        unique IDs to each challenge and flag, and sets the necessary attributes
        such as name, description, category, and content.

        Note: The method assumes that the `descriptions`, `categories`, and `flags`
        dictionaries have already been populated with the necessary data, and are of equal size.

        Example:
            >>> self.__fill_flags_db_and_challenges_db()
        """
        self.__get_vuln_descriptions_and_categories_and_flags()

        #TODO: Check for same amount of challenges, flags and categories

        id = 0
        for vuln_name in self.descriptions:
            id += 1
            challenge = {
                "id": 1,
                "name": "__REPLACE_ME__",
                "description": "__REPLACE_ME__",
                "max_attempts": 0,
                "value": 1000,
                "category": "__REPLACE_ME__",
                "type": "standard",
                "state": "visible",
                "requirements": None,
                "connection_info": None,
                "next_id": None
            }
            challenge["id"] = id
            challenge["name"] = "Vulnerability " + str(id)
            challenge["description"] = self.descriptions[vuln_name]
            challenge["category"] = self.categories[vuln_name]
            self.challenges_db["results"].append(challenge)

            flag = {
                "id": 0,
                "challenge_id": 1,
                "type": "static",
                "content": "__REPLACE_ME__",
                "data": ""
            }
            flag["id"] = id
            flag["challenge_id"] = id
            flag["content"] = self.flags[vuln_name]
            self.flags_db["results"].append(flag)

        count = len(self.descriptions)
        self.challenges_db["count"] = count
        self.flags_db["count"] = count

    def __replace_ctfd_export_flags_and_descriptions(self) -> None:
        """
        Replaces challenge flags and descriptions in the CTFd export zip file by extracting, modifying, and re-packing it.

        Example:
            >>> self.__replace_ctfd_export_flags_and_descriptions()
        """
        pulumi.log.info("Replacing challenge flags and descriptions in CTFd export")
        temp_dir = "ctfd_export_temp_dir/"
        db_path = "ctfd_export_temp_dir/db/"

        ctfd_export_path = self.ctfd_path + "/ctfd_export.zip"
        self.__unzip_file(ctfd_export_path, temp_dir)

        self.__fill_flags_db_and_challenges_db()
        self.__write_json(db_path + "flags.json", self.flags_db)
        self.__write_json(db_path + "challenges.json", self.challenges_db)

        self.__zip_dir(temp_dir, self.ctfd_path + "/ctfd_export") # shutil adds .zip to the filename
        self.__delete_dir(temp_dir)
