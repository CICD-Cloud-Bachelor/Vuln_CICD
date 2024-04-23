import pulumi_azure as azure
import pulumi
from vulnerabilities.vuln3 import main as vuln3
from vulnerabilities.vuln2 import main as vuln2
from vulnerabilities.vuln4 import main as vuln4
from vulnerabilities.vuln5 import main as vuln5
from source.create_azure_devops import CreateAzureDevops
from source.config import LOCATION
from source.CTFdContainer import CtfdContainer
from faker import Faker

faker = Faker()
username = faker.name().replace('.', ' ')
password = CreateAzureDevops.random_password()
entra_user = CreateAzureDevops.create_entra_user(username, password)
user = {
    "entra_user": entra_user, 
    "username": username
}


resource_group = azure.core.ResourceGroup('resource-group', location=LOCATION)


#vuln2.start()


vuln4.start(resource_group, entra_user)

#vuln5.start(resource_group, user)

#ctfd = CtfdContainer(username, password)

