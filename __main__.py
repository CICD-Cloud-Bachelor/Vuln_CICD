import pulumi_azure as azure
from pulumi import Config
from vulnerabilities.vuln3 import main as vuln3

resource_group = azure.core.ResourceGroup('resource-group_mo', location="West Europe")

vuln3.start(resource_group)
