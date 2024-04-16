import pulumi_azure as azure
from pulumi import Config
#from vulnerabilities.vuln1 import main as vuln1
import source.container as test_container
from vulnerabilities.vuln2 import main as vuln2
from vulnerabilities.vuln4 import main as vuln4
from vulnerabilities.vuln5 import main as vuln5
from source.config import LOCATION
from pulumi import Config


resource_group = azure.core.ResourceGroup('resource-group', location=LOCATION)

#ctf = test_container.CtfdContainer()

#vuln1.start(resource_group)
vuln5.start(resource_group)
#vuln4.start(resource_group)
#vuln5.start(resource_group)
