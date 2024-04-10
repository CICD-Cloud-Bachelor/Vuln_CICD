import pulumi_azure as azure
import pulumi
from vulnerabilities.vuln3 import main as vuln3
from source.container import CtfdContainer

resource_group = azure.core.ResourceGroup('resource-group_mo', location="West Europe")

vuln3.start(resource_group)

# Start ctfd container 
#
ctfd = CtfdContainer()
#