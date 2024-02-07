from faker import Faker
import pulumi
import pulumi_azuredevops as azuredevops
from pulumi_azuread import User



class CreateUsers:
    fake = Faker()
    
    def __init__(self, domain: str) -> None:
        self.domain = domain

    def __create_entra_user(self, name: str, password: str) -> None:
        pulumi.log.info(f"Creating user in Azure AD (Entra): {name}")
        self.entra_user = User(f"{name}",
                                display_name = name,
                                user_principal_name = f"{name.replace(' ', '.')}@{self.domain}",
                                password = password,
                                force_password_change = False # Set to True if you want to force a password change on first login
                                )
        pulumi.export(f"{name}_entra_user_id", self.entra_user.id)

    def create_devops_user(self, name: str, password: str) -> User:
        self.__create_entra_user(name, password)

        pulumi.log.info(f"Creating user in Azure DevOps: {name}")
        self.devops_user = azuredevops.User(f"{name}",
                                    principal_name = self.entra_user.user_principal_name
                                    )
        pulumi.export(f"{name}_devops_user_id", self.devops_user.id)
        return self.devops_user

    def __randomPass(self) -> str:
        return self.fake.password(length=10, special_chars=True, digits=True, upper_case=True, lower_case=True)

