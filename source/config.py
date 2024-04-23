import configparser

config = configparser.ConfigParser()
config.read('config.ini')
USERNAME                    = config["AZURE"]["USERNAME"]
ORGANIZATION_NAME           = config["AZURE"]["ORGANIZATION_NAME"]
DOMAIN                      = config["AZURE"]["DOMAIN"]
PAT                         = config["AZURE"]["PAT"]
LOCATION                    = config["AZURE"]["LOCATION"]
STORAGE_ACCOUNT_NAME        = config["AZURE"]["STORAGE_ACCOUNT_NAME"]
STORAGE_CONTAINER_NAME      = config["AZURE"]["STORAGE_CONTAINER_NAME"]
GITHUB_PAT                  = config["GITHUB"]["PAT"]
DNS_LABEL                   = config["DOCKER"]["DNS_LABEL"]
REGISTRY_NAME               = config["DOCKER"]["REGISTRY_NAME"]
CONTAINER_PATH              = config["DOCKER"]["CONTAINER_PATH"]

