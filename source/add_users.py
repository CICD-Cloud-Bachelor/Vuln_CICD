from faker import Faker
import pulumi
from pulumi_azuread import User



class CreateUsers:
    fake = Faker()
    
    def __init__(self, domain: str) -> None:
        self.domain = domain

    def create_user(self, name: str, password: str) -> User:
        pulumi.log.info(f"Creating user in Azure AD: {name}")
        self.user_object = User(f"{name}",
                                    display_name = name,
                                    user_principal_name = f"{name.replace(' ', '.')}@{self.domain}",
                                    password = password,
                                    force_password_change = False # Set to True if you want to force a password change on first login
                                    )
        pulumi.export(f"{name}_object_id", self.user_object.id)
        return self.user_object

    def __randomPass(self) -> str:
        return self.fake.password(length=10, special_chars=True, digits=True, upper_case=True, lower_case=True)

