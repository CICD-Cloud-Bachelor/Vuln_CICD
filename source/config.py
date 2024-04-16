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
DNS_LABEL                   = config["DOCKER"]["DNS_LABEL"]
REGISTRY_NAME               = config["DOCKER"]["REGISTRY_NAME"]
CONTAINER_PATH              = config["DOCKER"]["CONTAINER_PATH"]
FLAG1                       = config["FLAGS"]["VULN1"]
FLAG2                       = config["FLAGS"]["VULN2"]
FLAG3                       = config["FLAGS"]["VULN3"]
FLAG4                       = config["FLAGS"]["VULN4"]
FLAG5                       = config["FLAGS"]["VULN5"]
CHALL1                      = config["CHALLENGES"]["CHALL1"]
CHALL2                      = config["CHALLENGES"]["CHALL2"]
CHALL3                      = config["CHALLENGES"]["CHALL3"]
CHALL4                      = config["CHALLENGES"]["CHALL4"]
CHALL5                      = config["CHALLENGES"]["CHALL5"]
