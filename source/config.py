"""
A random sequence of bytes are appended to values required to be unique in the Azure environment.
"""

import configparser, os

config = configparser.ConfigParser()
config.read('config.ini')
USERNAME                    = config["AZURE"]["USERNAME"]
ORGANIZATION_NAME           = config["AZURE"]["ORGANIZATION_NAME"]
DOMAIN                      = config["AZURE"]["DOMAIN"]
PAT                         = config["AZURE"]["PAT"]
LOCATION                    = config["AZURE"]["LOCATION"]
STORAGE_ACCOUNT_NAME        = config["AZURE"]["STORAGE_ACCOUNT_NAME"] + os.urandom(5).hex()
STORAGE_CONTAINER_NAME      = config["AZURE"]["STORAGE_CONTAINER_NAME"] + os.urandom(5).hex()
GITHUB_PAT                  = config["GITHUB"]["PAT"]
DNS_LABEL                   = config["DOCKER"]["DNS_LABEL"] + os.urandom(5).hex()
REGISTRY_NAME               = config["DOCKER"]["REGISTRY_NAME"] + os.urandom(5).hex()
CONTAINER_PATH              = config["DOCKER"]["CONTAINER_PATH"]

