from faker import Faker
import pulumi
from pulumi_azuread import User



class CreateSpecificUser:
    """
    A class for creating a specific user and adding them to Azure AD.

    Args:
        display_name (str): The display name of the user.
        user_principal_name (str): The user principal name of the user.
        password (str): The password of the user.
    """
    domain = "bacheloroppgave2024proton.onmicrosoft.com"

    def __init__(self, display_name: str, password: str) -> None:
        self.display_name = display_name
        self.user_principal_name = f"{display_name.replace(' ', '.')}@{self.domain}"
        self.password = password
        self.create_user_in_azure_ad()

    def create_user_in_azure_ad(self):
        """
        Create the user in Azure AD.
        """
        pulumi.log.debug(f"Creating user in Azure AD")
        user_object = User("specific_user",
                        display_name=self.display_name,
                        user_principal_name=self.user_principal_name,
                        password=self.password,
                        force_password_change=False # Set to True if you want to force a password change on first login
                        )
        
        pulumi.log.debug(f"Created user: {user_object.display_name}")

class CreateRandomUsers:
    """
    A class for creating random users and adding them to Azure AD.

    Args:
        amount (int): The number of users to create.
    """

    fake = Faker()
    domain = "bacheloroppgave2024proton.onmicrosoft.com"
    user_details = []
    
    def __init__(self, amount: int) -> None:
        self.amount = amount
        self.create_users()
        self.create_users_in_azure_ad()

    def create_users(self) -> None:
        """
        Create the specified number of users with random names and passwords.
        """
        pulumi.log.debug(f"Creating {self.amount} users")
        for _ in range(self.amount):
            name = self.fake.name()
            pulumi.log.debug(f"Creating user: {name}")
            self.user_details.append({"display_name": name, "user_principal_name": f"{name.replace(' ', '.')}@{self.domain}", "password": self.fake.password(length=10, special_chars=True, digits=True, upper_case=True, lower_case=True)})

    def create_users_in_azure_ad(self):
        """
        Create the users in Azure AD.
        """
        pulumi.log.debug(f"Creating users in Azure AD")
        for index, user in enumerate(self.user_details):
            user_object = User(f"user{index}",
                            display_name=user["display_name"],
                            user_principal_name=user["user_principal_name"],
                            password=user["password"],
                            force_password_change=False # Set to True if you want to force a password change on first login
                            )
            
            pulumi.log.debug(f"Created user: {user_object.display_name}")

