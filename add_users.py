from faker import Faker
import pulumi
from pulumi_azuread import User



class CreateUsers:
    fake = Faker()
    domain = "bacheloroppgave2024proton.onmicrosoft.com"
    user_details = []
    
    def __init__(self, amount: int) -> None:
        self.amount = amount
        self.create_users()
        self.create_users_in_azure_ad()

    def create_users(self) -> None:
        pulumi.log.debug(f"Creating {self.amount} users")
        for _ in range(self.amount):
            name = self.fake.name()
            pulumi.log.debug(f"Creating user: {name}")
            self.user_details.append({"display_name": name, "user_principal_name": f"{name.replace(' ', '.')}@{self.domain}", "password": self.fake.password(length=10, special_chars=True, digits=True, upper_case=True, lower_case=True)})

    def create_users_in_azure_ad(self):
        pulumi.log.debug(f"Creating users in Azure AD")
        for index, user in enumerate(self.user_details):
            user_object = User(f"user{index}",
                            display_name=user["display_name"],
                            user_principal_name=user["user_principal_name"],
                            password=user["password"],
                            force_password_change=False # Set to True if you want to force a password change on first login
                            )
            
            pulumi.log.debug(f"Created user: {user_object.display_name}")
            pulumi.export(f"user{index}_object_id", user_object.id)


