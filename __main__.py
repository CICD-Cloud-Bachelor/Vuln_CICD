import pulumi_azure as azure
from vulnerabilities.vuln3 import main

resource_group = azure.core.ResourceGroup(
    'resource-group', 
    location="West Europe"
)
main.start(resource_group)
