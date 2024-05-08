import pulumi_azure as azure
import pulumi
from vulnerabilities.vuln1 import main as vuln1
from vulnerabilities.vuln2 import main as vuln2
from vulnerabilities.vuln3 import main as vuln3
from vulnerabilities.vuln4 import main as vuln4
from vulnerabilities.vuln5 import main as vuln5
from source.create_azure_devops import CreateAzureDevops
from source.container import DockerACR
from source.config import LOCATION, DOMAIN
from source.CTFdContainer import CTFdContainer
from faker import Faker


####################################################################
#             CREATING USER IN ENTRA ID AND DEVOPS                 #
####################################################################
username = Faker().name().replace('.', ' ')
password = CreateAzureDevops.random_password()
entra_user = CreateAzureDevops.create_entra_user(username, password)
entra_user_dict = {
    "entra_user": entra_user, 
    "username": username
}
devops_user = CreateAzureDevops.add_entra_user_to_devops(entra_user_dict)
####################################################################

resource_group = azure.core.ResourceGroup('resource-group', location=LOCATION)

acr = DockerACR(
    resource_group=resource_group, 
)

#vuln1.start(resource_group, devops_user)
vuln2.start(resource_group, devops_user, acr)
#vuln3.start(resource_group, devops_user)
#vuln4.start(resource_group, devops_user, acr)
#vuln5.start(resource_group, devops_user, acr)

# if not pulumi.runtime.is_dry_run(): # check if preview is running
CTFd = CTFdContainer(username, password, acr)

