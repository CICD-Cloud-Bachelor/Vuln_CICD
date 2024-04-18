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

    def __init__(self, username: str, password: str):
        """
        Initializes a new instance of the CtfdContainer class.

        This method sets the ctfd_path attribute and replaces challenge flags and descriptions
        in the CTFd export zip file. It then runs the docker-compose command to start the container.
        """
        self.entra_username = username
        self.entra_password = password
        self.ctfd_path = f"{CONTAINER_PATH}/CTFd"
        self.__replace_chall_flags_and_descriptions(self.ctfd_path)
        self.__run_docker_compose(['--project-directory', self.ctfd_path, 'up', '-d'])

    def __run_docker_compose(self, command: list[str]):
        """
        Runs a docker-compose command and prints its output.

        :param command: List of the command parts, e.g., ['up', '-d'] for 'docker-compose up -d'.
        """
        pulumi.log.info("Starting CTFd container")
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
    
    def __get_descriptions(self) -> dict:
        
        vuln_folders = [folder for folder in os.listdir('vulnerabilities/') if folder.startswith('vuln')]
        number_of_vulns = len(vuln_folders)

        vuln_modules = []
        for i in range(number_of_vulns):
            vuln_modules.append(f"vulnerabilities.vuln{i+1}.main")

        descriptions = {}

        for module_name in vuln_modules:
            module = importlib.import_module(module_name)
            vuln = module.__name__.replace("vulnerabilities.", "").replace(".main", "")
            descriptions[vuln] = module.CHALLENGE_DESCRIPTION + f'\n\nLogin: {self.entra_username}\nPassword: {self.entra_password}\n<a href="https://dev.azure.com/{ORGANIZATION_NAME}">Link</a>'
            
        return descriptions
    
    def __replace_chall_flags_and_descriptions(self, ctfd_path: str) -> None:
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

        descriptions = self.__get_descriptions()
        new_flags_dict = self.__replace_flags(old_flags, flags)
        new_challs_dict = self.__replace_descriptions(old_challs, descriptions)

        self.__write_json(db_path + "flags.json", new_flags_dict)
        self.__write_json(db_path + "challenges.json", new_challs_dict)

        self.__zip_dir(temp_dir, ctfd_path + "/ctfd_export") # shutil adds .zip to the filename
        self.__delete_dir(temp_dir)