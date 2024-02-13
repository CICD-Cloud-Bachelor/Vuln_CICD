import pulumi_azure as azure
from pulumi import Config
#from vulnerabilities.vuln1 import main as vuln1
#from vulnerabilities.vuln4 import main as vuln4
from vulnerabilities.vuln5 import main as vuln5

from pulumi import Config

config = Config("azure-native")
location = config.get("location")
resource_group = azure.core.ResourceGroup('resource-group', location=location)



#vuln1.start()

#vuln4.start(resource_group)
vuln5.start(resource_group)
