import pulumi_azure as azure
import pulumi
from vulnerabilities.vuln2 import main as vuln2
#from vulnerabilities.vuln3 import main as vuln3
from source.create_azure_devops import CreateAzureDevops
from source.config import LOCATION
from source.CTFdContainer import CtfdContainer
from faker import Faker

#faker = Faker()
#username = faker.name().replace('.', ' ')
#password = CreateAzureDevops.random_password()

resource_group = azure.core.ResourceGroup('resource-group', location=LOCATION)


# entra_user = CreateAzureDevops.create_entra_user(username, password)

# vuln3.start(resource_group, entra_user)

#ctfd = CtfdContainer(username, password)

vuln2.start(resource_group)


