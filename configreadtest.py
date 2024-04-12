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

zip_file = "source/docker_images/CTFd/ctfd_export.zip"
extract_dir = "ctfd_temp_dir/"

with zipfile.ZipFile(zip_file, 'r') as zip_ref:
    zip_ref.extractall(extract_dir)


json_file = extract_dir + "db/" + "flags.json"
with open(json_file, 'r') as f:
    data = json.load(f)

print(data["results"])

# Replace the placeholder flags with the actual flags
for flagentry in data["results"]:
    index = flagentry["id"] - 1
    flag = flags[index]
    flagentry["content"] = flag

print(data["results"])
shutil.rmtree(extract_dir)