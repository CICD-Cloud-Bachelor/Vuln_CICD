import pulumi_azure as azure
<<<<<<< HEAD

from vulnerabilities.vuln1 import main as vuln1
from vulnerabilities.vuln2 import main as vuln2
=======
from pulumi import Config
#from vulnerabilities.vuln1 import main as vuln1
>>>>>>> Dev
from vulnerabilities.vuln4 import main as vuln4
#from vulnerabilities.vuln5 import main as vuln5

config = Config("azure-native")
location = config.get("location")
resource_group = azure.core.ResourceGroup('resource-group', location=location)



#vuln1.start()
<<<<<<< HEAD
vuln2.start(resource_group)
#vuln4.start(resource_group)
#vuln5.start(resource_group)
=======

vuln4.start(resource_group)
#vuln5.start(resource_group)
>>>>>>> Dev
