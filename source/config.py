import pulumi
import configparser

pulumi_config = pulumi.Config("azuredevops")
pulumi_azure_native_config = pulumi.Config("azure-native")
PAT = pulumi_config.get("personalAccessToken")
LOCATION = pulumi_azure_native_config.require("location")

config = configparser.ConfigParser()
config.read('config.ini')
USERNAME = config["AZURE"]["USERNAME"]
ORGANIZATION_NAME = config["AZURE"]["ORGANIZATION_NAME"]
DOMAIN = config["AZURE"]["PRINCIPLE_NAME"]
DNS_LABEL = config["DOCKER"]["DNS_LABEL"]
REGISTRY_NAME = config["DOCKER"]["REGISTRY_NAME"]
FLAG1 = config["FLAGS"]["VULN1"]
FLAG2 = config["FLAGS"]["VULN2"]
FLAG3 = config["FLAGS"]["VULN3"]
FLAG4 = config["FLAGS"]["VULN4"]
FLAG5 = config["FLAGS"]["VULN5"]