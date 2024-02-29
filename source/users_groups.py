from faker import Faker
import pulumi
import pulumi_azuredevops as azuredevops
import configparser
import os
from pulumi_azuread import User
import docker
import json 

config = configparser.ConfigParser()
config.read('config.ini')
DOMAIN = config["AZURE"]["DOMAIN"]

class UserCreator:
    def create_entra_user(
            name: str, 
            password: str) -> User:
        """
        Creates a user in Entra (Azure AD).

        Args:
            name (str): The name of the user.
            password (str): The password for the user.

        Returns:
            None
        """
        pulumi.log.info(f"Creating user in Entra (Azure AD): {name}")
        entra_user = User(f"{name}",
            display_name = name,
            user_principal_name = f"{name.replace(' ', '.')}@{DOMAIN}",
            password = password,
            force_password_change = False # Set to True if you want to force a password change on first login
            )

        return entra_user

    def create_devops_user(
            name: str, 
            password: str) -> azuredevops.User:
        """
        Creates a user in Azure DevOps. Max 5 Users in free plan.

        Args:
            name (str): The name of the user.
            password (str): The password for the user.

        Returns:
            User: The created user object in Azure DevOps.
        """

        entra_user = UserCreator.create_entra_user(name, password)

        pulumi.log.info(f"Creating user in Azure DevOps: {name}")
        devops_user = azuredevops.User(f"{name}",
            principal_name = entra_user.user_principal_name
            )

        return devops_user

    def randomPass() -> str:
        return Faker().password(length=10, special_chars=True, digits=True, upper_case=True, lower_case=True)

class GroupCreator:

    def create_group(
            project: azuredevops.Project, 
            group_name: str) -> azuredevops.Group:
        """
        Creates an Azure DevOps group.

        Args:
            project (azuredevops.Project): The Azure DevOps project.
            group_name (str): The name of the group.

        Returns:
            azuredevops.Group: The created Azure DevOps group.
        """
        pulumi.log.info(f"Creating Azure DevOps group: {group_name}")
        group = azuredevops.Group(f"customGroup_{group_name}",
            scope=project.id,
            display_name=group_name,
            description="Custom made permissions for devops"
        )
        return group

    def add_user_to_group(
            user: azuredevops.User, 
            group: azuredevops.Group) -> None:
        """
        Adds a user to a group in Azure DevOps.

        Args:
            user (azuredevops.User): The user to be added.
            group (azuredevops.Group): The group to add the user to.

        Returns:
            None
        """
        pulumi.log.info("Adding user to group")
        azuredevops.GroupMembership("groupMembership_" + os.urandom(5).hex(),
            group=group.descriptor,
            members=[user.descriptor]
        )
    
    def modify_project_permission(
            project: azuredevops.Project, 
            group: azuredevops.Group, 
            permissions: dict) -> None:
        """
        Modifies the project permissions for a specific group.

        Args:
            project (azuredevops.Project): The project to modify permissions for.
            group (azuredevops.Group): The group to modify permissions for.
            permissions (dict): The permissions to assign to the group.

        Returns:
            None
        """
        
        azuredevops.ProjectPermissions("projectPermissions_" + os.urandom(5).hex(),
            project_id=project.id,
            principal=group.id,
            permissions=permissions
        )
        # Link to permissions overview https://www.pulumi.com/registry/packages/azuredevops/api-docs/projectpermissions/

    def modify_pipeline_permissions(
            project: azuredevops.Project, 
            group: azuredevops.Group, 
            pipeline: azuredevops.BuildDefinition, 
            permissions: dict) -> None:
        """
        Modifies the pipeline permissions for a specific group.

        Args:
            project (azuredevops.Project): The Azure DevOps project.
            group (azuredevops.Group): The Azure DevOps group.
            pipeline (azuredevops.BuildDefinition): The Azure DevOps pipeline.
            permissions (dict): The permissions to be set for the group.

        Returns:
            None
        """
        pulumi.log.info("Modifying pipeline permissions for group")
        azuredevops.BuildDefinitionPermissions("pipelinePermissions_" + os.urandom(5).hex(),
            project_id=project.id,
            principal=group.id,
            build_definition_id=pipeline.id,
            permissions=permissions
            # link to doc page with permissions https://www.pulumi.com/registry/packages/azuredevops/api-docs/builddefinitionpermissions/
        )
    
    def modify_repository_permissions(
            project: azuredevops.Project, 
            group: azuredevops.Group, 
            repository: azuredevops.Git, 
            permissions: dict) -> None:
        """
        Modifies the git repository level permissions for a specific group. Applied to all branches.

        Args:
            project (azuredevops.Project): The Azure DevOps project.
            group (azuredevops.Group): The Azure DevOps group.
            repository (azuredevops.Repository): The Azure DevOps repository.
            permissions (dict): The permissions to be set for the group.

        Returns:
            None
        """
        pulumi.log.info("Modifying git repository permissions for group")
        azuredevops.GitPermissions("repositoryPermissions_" + os.urandom(5).hex(),
            project_id=project.id,
            principal=group.id,
            repository_id=repository.id,
            permissions=permissions
            # link to doc page with permissions https://www.pulumi.com/registry/packages/azuredevops/api-docs/gitpermissions/
        )
    
    def modify_branch_permissions(
            project: azuredevops.Project, 
            group: azuredevops.Group, 
            repository: azuredevops.Git, 
            branch: str, 
            permissions: dict) -> None:
        """
        Modifies the git branch level permissions for a specific group.

        Args:
            project (azuredevops.Project): The Azure DevOps project.
            group (azuredevops.Group): The Azure DevOps group.
            repository (azuredevops.Repository): The Azure DevOps repository.
            branch (str): The name of the branch.
            permissions (dict): The permissions to be set for the group.

        Returns:
            None
        """
        pulumi.log.info("Modifying git branch permissions for group")
        azuredevops.GitPermissions("branchPermissions_" + os.urandom(5).hex(),
            project_id=project.id,
            principal=group.id,
            repository_id=repository.id,
            branch_name=branch,
            permissions=permissions
            # link to doc page with permissions https://www.pulumi.com/registry/packages/azuredevops/api-docs/gitpermissions/
        )

    def modify_area_permissions(
        project: azuredevops.Project,
        group: azuredevops.Group,
        permissions: dict
    ) -> None:
        """
        Modifies the area permissions for a specific group.

        Args:
            project (azuredevops.Project): The Azure DevOps project.
            group (azuredevops.Group): The Azure DevOps group.
            permissions (dict): The permissions to be set for the group.

        Returns:
            None
        """
        pulumi.log.info("Modifying area permissions for group")
        azuredevops.AreaPermissions("areaPermissions_" + os.urandom(5).hex(),
            project_id=project.id,
            principal=group.id,
            path="/",
            permissions=permissions
            # link to doc page with permissions https://www.pulumi.com/registry/packages/azuredevops/api-docs/areapermissions/
        )

class GenerateToken:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    def create_token(self) -> None:
        """
        Creates an access token by logging in to Azure CLI using the provided username and password.
        The access token is obtained from the Azure CLI container and printed to the console.
        This token w
        Args:
            None
        """
        client = docker.from_env()
        
        image_name = "mcr.microsoft.com/azure-cli"
        image = client.images.pull(image_name)

        # Create a container from the pulled image
        container = client.containers.create(image_name, command="tail -f /dev/null", detach=True)

        # Start the containerq
        container.start()

        exec_login = container.exec_run(f'az login --username {self.username} --password {self.password} --allow-no-subscriptions')
        get_token = container.exec_run(f'az account get-access-token')

        output = get_token.output.decode('utf-8')

        json_output = json.loads(output)

        self.token = json_output["accessToken"]

        container.stop()
        container.remove()
    
    def get_token(self) -> str:
        return self.token