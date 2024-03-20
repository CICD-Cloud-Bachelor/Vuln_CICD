import pulumi_azure as azure
from pulumi import Config
from vulnerabilities.vuln4 import fromdeorepo


from pulumi import Config


resource_group = azure.core.ResourceGroup('mo-resource_group', location="West Europe")



fromdeorepo.start(resource_group)

