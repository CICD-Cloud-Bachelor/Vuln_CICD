import pulumi_azure as azure
import pulumi
from vulnerabilities.vuln3 import main as vuln3
from source.container import CtfdContainer
from vulnerabilities.vuln1 import main as vuln1
from vulnerabilities.vuln4 import main as vuln4
from vulnerabilities.vuln5 import main as vuln5
from source.config import LOCATION


#resource_group = azure.core.ResourceGroup('resource-group_mo', location="West Europe")

#vuln3.start(resource_group)

ctfd = CtfdContainer()

resource_group = azure.core.ResourceGroup('resource-group', location=LOCATION)



#vuln1.start(resource_group)

#vuln3.start(resource_group)
#vuln5.start(resource_group)





#vuln4.start(resource_group)
