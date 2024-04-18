import configparser
import importlib
import os
from source.config import *

login = "admin"
password = "admin"


vuln_folders = [folder for folder in os.listdir('vulnerabilities/') if folder.startswith('vuln')]
number_of_vulns = len(vuln_folders)

vuln_modules = []
for i in range(number_of_vulns):
    vuln_modules.append(f"vulnerabilities.vuln{i+1}.main")

descriptions = {}

for module_name in vuln_modules:
    module = importlib.import_module(module_name)
    vuln = module.__name__.replace("vulnerabilities.", "").replace(".main", "")
    descriptions[vuln] = module.CHALLENGE_DESCRIPTION + f'\n\nLogin: {login}\nPassword: {password}\n<a href="https://dev.azure.com/{ORGANIZATION_NAME}">Link</a>'
    
print(descriptions)

# with open('config.ini', 'w') as configfile:
#     config.write(configfile)

