"""
A random 5 byte sequence of bytes are appended to values required to be unique in the Azure environment.
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

# import os

# USERNAME =                  os.getenv("USERNAME")
# ORGANIZATION_NAME =         os.getenv("ORGANIZATION_NAME")
# DOMAIN =                    os.getenv("DOMAIN")
# PAT =                       os.getenv("DEVOPS_PAT")
# LOCATION =                  os.getenv("LOCATION", "westeurope")
# STORAGE_ACCOUNT_NAME =      os.getenv("STORAGE_ACCOUNT_NAME", "storaccount") + os.urandom(5).hex()
# STORAGE_CONTAINER_NAME =    os.getenv("STORAGE_CONTAINER_NAME", "storcontainer") + os.urandom(5).hex()
# GITHUB_PAT =                os.getenv("GITHUB_PAT", "NULL")
# DNS_LABEL =                 os.getenv("DNS_LABEL", "pulumibachelorproject") + os.urandom(5).hex()
# REGISTRY_NAME =             os.getenv("REGISTRY_NAME", "registrypulumi") + os.urandom(5).hex()
# CONTAINER_PATH =            "source/docker_images/"
