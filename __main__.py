import pulumi_azure as azure
import pulumi
from vulnerabilities.vuln3 import main as vuln3
from source.container import CtfdContainer
from source.config import LOCATION

resource_group = azure.core.ResourceGroup('resource-group', location=LOCATION)


vuln3.start(resource_group)

#ctfd = CtfdContainer()

