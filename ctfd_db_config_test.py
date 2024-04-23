import zipfile
import shutil
import json
import importlib
import os
import copy
from source.config import *

db_template = {
    "count": 0,
    "results": [],
    "meta": {}
}
flags_entry_template = {
    "id": 1,
    "challenge_id": 1,
    "type": "static",
    "content": "1111",
    "data": ""
}
challenges_entry_template = {
    "id": 1,
    "name": "Vulnerability X",
    "description": "",
    "max_attempts": 0,
    "value": 1000,
    "category": "Easy",
    "type": "standard",
    "state": "visible",
    "requirements": None,
    "connection_info": None,
    "next_id": None
}

def add_challenges_to_db(db: dict, challenges: list):
    pass

def write_json(file: str, data: dict):
    with open(file, 'w') as f:
        json.dump(data, f)

def get_vuln_descriptions_and_categories():
    vuln_folders = [folder for folder in os.listdir('vulnerabilities/') if folder.startswith('vuln')]
    number_of_vulns = len(vuln_folders)

    vuln_modules = []
    for i in range(number_of_vulns):
        vuln_modules.append(f"vulnerabilities.vuln{i+1}.main")

    descriptions = {}
    categories = {}
    for vuln_name in vuln_modules:
        vuln = importlib.import_module(vuln_name)
        vuln_key = vuln.__name__.replace("vulnerabilities.", "").replace(".main", "")
        descriptions[vuln_key] = vuln.CHALLENGE_DESCRIPTION + f'\n\nLogin: AAAA\n\nPassword: BBBB\n\n<a href="https://dev.azure.com/{ORGANIZATION_NAME}">Link</a>'
        categories[vuln_key] = vuln.CHALLENGE_CATEGORY

    return descriptions, categories

if __name__ == '__main__':
    # descriptions, categories = get_vuln_descriptions_and_categories()

    # challenges_db = copy.deepcopy(db_template)
    # flags_db = copy.deepcopy(db_template)
    
    # id = 0
    # for vuln_name in descriptions:
    #     id += 1
    #     challenge = copy.deepcopy(challenges_entry_template)
    #     challenge["id"] = id
    #     challenge["name"] = "Vulnerability " + str(id)
    #     challenge["description"] = descriptions[vuln_name]
    #     challenge["category"] = categories[vuln_name]
    #     challenges_db["results"].append(challenge)

    #     flag = copy.deepcopy(flags_entry_template)
    #     flag["id"] = id
    #     flag["challenge_id"] = id
    #     flag["content"] = FLAGS[vuln_name]
    #     flags_db["results"].append(flag)

    # write_json("challenges.json", challenges_db)
    # write_json("flags.json", flags_db)
    pass





