import configparser
import zipfile
import json
import shutil

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

#####
# A heads up - The code assumes the ctfd_export template has the challenges set up with placeholder flags.
# This is so that the flags json file has an entry for the respective challenges.
# The default ctfd_export.zip has 5 challenges configured, with their id being 1-5 respectively.
#####

def unzip_file(zip_file: str, extraction_dir: str) -> None:
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(extraction_dir)

def delete_dir(dir: str) -> None:
    shutil.rmtree(dir)

def read_json(file: str) -> dict:
    with open(file, 'r') as f:
        data = json.load(f)
    return data

def write_json(file: str, data: dict) -> None:
    with open(file, 'w') as f:
        json.dump(data, f)

def replace_flags(flag_dict: dict, flags: list) -> None:              
    for flag_entry in flag_dict["results"]:
        index = flag_entry["id"] - 1
        flag = flags[index]
        flag_entry["content"] = flag
    return flag_dict

def replace_descriptions(chall_dict: dict, descriptions: list) -> None:
    for chall_entry in chall_dict["results"]:
        index = chall_entry["id"] - 1
        description = descriptions[index]
        chall_entry["description"] = description
    return chall_dict

if __name__ == "__main__":
    zip_file = "source/docker_images/CTFd/ctfd_export.zip"
    temp_dir = "ctfd_temp_dir/"
    db_path = "ctfd_temp_dir/db/"

    unzip_file(zip_file, temp_dir)

    flags_dict = read_json(db_path + "flags.json")
    challs_dict = read_json(db_path + "challenges.json")

    new_flags_dict = replace_flags(flags_dict, flags)
    new_challs_dict = replace_descriptions(challs_dict, descriptions)

    write_json(db_path + "flags.json", new_flags_dict)
    write_json(db_path + "challenges.json", new_challs_dict)
    
    delete_dir(temp_dir)