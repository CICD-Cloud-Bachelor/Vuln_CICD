import pulumi
import zipfile
import shutil
import json
import subprocess
import importlib
import os
from source.config import *

class CtfdContainer:
    """
    Represents a CTFd container.

    This class provides methods to initialize and manage a CTFd container. It allows replacing challenge flags and descriptions in the CTFd export zip file, running the container using docker-compose, and performing other related operations.

    Attributes:
        flags_db (dict): The database of challenge flags.
        challenges_db (dict): The database of challenges.
        descriptions (dict): A dictionary to store vulnerability descriptions.
        categories (dict): A dictionary to store vulnerability categories.
        flags (dict): A dictionary to store vulnerability flags.
        login_name (str): The login name for the Azure DevOps user.
        entra_password (str): The password for the Azure DevOps user.
        ctfd_path (str): The path to the CTFd container directory.

    Methods:
        __init__(self, username: str, password: str): Initializes a new instance of the CtfdContainer class.
        __run_docker_compose(self, command: list[str]): Runs a docker-compose command and prints its output.
        __unzip_file(self, zip_file: str, extraction_dir: str) -> None: Extracts a zip file to the specified directory.
        __zip_dir(self, dir: str, zip_file: str) -> None: Zips a directory and its contents.
        __delete_dir(self, dir: str) -> None: Deletes a directory and its contents.
        __write_json(self, file: str, data: dict) -> None: Writes a dictionary to a JSON file.
        __get_vuln_descriptions_and_categories_and_flags(self) -> None: Retrieves vulnerability descriptions, categories, and flags for each vulnerability module.
        __fill_flags_db_and_challenges_db(self) -> None: Fills the flags and challenges databases with the necessary data.
        __make_files_executable(self, path: list[str]) -> None: Changes the permissions of a list of files.
        __replace_ctfd_export_flags_and_descriptions(self, ctfd_path: str) -> None: Replaces the challenge flags and descriptions in the CTFd export zip file.
    """
    
    def __init__(self, username: str, password: str):
        """
        Initializes a new instance of the CtfdContainer class.

        This method sets the ctfd_path attribute and replaces challenge flags and descriptions
        in the CTFd export zip file. It then runs the docker-compose command to start the container.

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
        self.descriptions = {}
        self.categories = {}
        self.flags = {}
        self.login_name = f"{username.replace(' ', '.')}@{DOMAIN}"
        self.entra_password = password
        self.ctfd_path = f"{CONTAINER_PATH}/CTFd"
        self.__replace_ctfd_export_flags_and_descriptions(self.ctfd_path)
        self.__run_docker_compose(['--project-directory', self.ctfd_path, 'up', '-d'])

    def __run_docker_compose(self, command: list[str]):
        """
        Runs a docker-compose command and prints its output.

        :param command: List of the command parts, e.g., ['up', '-d'] for 'docker-compose up -d'.
        """
        pulumi.log.info("Starting CTFd container")
        # Ensure the command is prefixed with 'docker-compose'
        docker_compose_cmd = ['docker', 'compose'] + command

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

    def __write_json(self, file: str, data: dict) -> None:
        """
        Writes a dictionary to a JSON file.

        :param file: The path to the JSON file.
        :param data: The dictionary to write to the file.
        """
        with open(file, 'w') as f:
            json.dump(data, f)
    
    def __get_vuln_descriptions_and_categories_and_flags(self) -> None:
        """
        Retrieves vulnerability descriptions, categories, and flags for each vulnerability module.

        This method iterates over the vulnerability modules and imports them dynamically using importlib.
        It then extracts the necessary information from each module and stores it in the respective dictionaries.

        Returns:
            None
        """
        vuln_folders = [folder for folder in os.listdir('vulnerabilities/') if folder.startswith('vuln')]
        number_of_vulns = len(vuln_folders)

        vuln_modules = []
        for i in range(number_of_vulns):
            vuln_modules.append(f"vulnerabilities.vuln{i+1}.main")

        for vuln_name in vuln_modules:
            vuln = importlib.import_module(vuln_name)
            vuln_key = vuln.__name__.replace("vulnerabilities.", "").replace(".main", "")
            self.descriptions[vuln_key] = vuln.CHALLENGE_DESCRIPTION + f'\n\nLogin: {self.login_name}\n\nPassword: {self.entra_password}\n\n<a href="https://dev.azure.com/{ORGANIZATION_NAME}">Link</a>'
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

        Returns:
            None
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

    def __make_files_executable(self, path: list[str]) -> None:
        """
        Changes the permissions of a list of files

        :param path: The list of paths to the files or directories.
        """
        for file_path in path:
            file_path = self.ctfd_path + "/" + file_path
            if os.path.exists(file_path):
                os.chmod(file_path, 0o755)
            else:
                print(f"File {file_path} does not exist.")

    def __replace_ctfd_export_flags_and_descriptions(self, ctfd_path: str) -> None:
        """
        Replaces the challenge flags and descriptions in the CTFd export zip file.

        :param ctfd_export_path: The path to the CTFd export zip file.
        """
        pulumi.log.info("Replacing challenge flags and descriptions in CTFd export")
        temp_dir = "ctfd_export_temp_dir/"
        db_path = "ctfd_export_temp_dir/db/"

        ctfd_export_path = ctfd_path + "/ctfd_export.zip"
        self.__unzip_file(ctfd_export_path, temp_dir)

        self.__fill_flags_db_and_challenges_db()
        self.__write_json(db_path + "flags.json", self.flags_db)
        self.__write_json(db_path + "challenges.json", self.challenges_db)

        self.__zip_dir(temp_dir, ctfd_path + "/ctfd_export") # shutil adds .zip to the filename
        self.__delete_dir(temp_dir)

        files_to_make_executable = [
            'docker-entrypoint.sh', 
            'prepare.sh', 
            'migrations/script.py.mako', 
            'scripts/pip-compile.sh'
        ]

        self.__make_files_executable(files_to_make_executable)