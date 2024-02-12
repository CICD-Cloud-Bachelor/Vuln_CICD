from faker import Faker
import pulumi
import pulumi_azuredevops as azuredevops
from pulumi_azuread import User



class UserCreator:
    fake = Faker()
    
    def __init__(self, domain: str) -> None:
        self.domain = domain

    def __create_entra_user(self, name: str, password: str) -> None:
            """
            Creates a user in Entra (Azure AD).

            Args:
                name (str): The name of the user.
                password (str): The password for the user.

            Returns:
                None
            """
            pulumi.log.info(f"Creating user in Entra (Azure AD): {name}")
            self.entra_user = User(f"{name}",
                display_name = name,
                user_principal_name = f"{name.replace(' ', '.')}@{self.domain}",
                password = password,
                force_password_change = False # Set to True if you want to force a password change on first login
                )
            pulumi.export(f"{name}_entra_user_id", self.entra_user.id)


    def create_devops_user(self, name: str, password: str) -> User:
            """
            Creates a user in Azure DevOps.

            Args:
                name (str): The name of the user.
                password (str): The password for the user.

            Returns:
                User: The created user object in Azure DevOps.
            """
            self.__create_entra_user(name, password)

            pulumi.log.info(f"Creating user in Azure DevOps: {name}")
            self.devops_user = azuredevops.User(f"{name}",
                principal_name = self.entra_user.user_principal_name
                )
            pulumi.export(f"{name}_devops_user_id", self.devops_user.id)
            return self.devops_user


    def __randomPass(self) -> str:
        return self.fake.password(length=10, special_chars=True, digits=True, upper_case=True, lower_case=True)


class GroupCreator:

    def create_group(project: azuredevops.Project, group_name: str) -> azuredevops.Group:
        """
        Creates an Azure DevOps group.

        Args:
            project (azuredevops.Project): The Azure DevOps project.
            group_name (str): The name of the group.

        Returns:
            azuredevops.Group: The created Azure DevOps group.
        """
        pulumi.log.info("Creating Azure DevOps group")
        group = azuredevops.Group("group",
            project_id=project.id,
            name=group_name,
            description=f"{group_name} group"
        )
        return group

    def add_user_to_group(user: azuredevops.User, group: azuredevops.Group) -> None:
        """
        Adds a user to a group in Azure DevOps.

        Args:
            user (azuredevops.User): The user to be added.
            group (azuredevops.Group): The group to add the user to.

        Returns:
            None
        """
        pulumi.log.info(f"Adding user to group")
        azuredevops.GroupMembership("groupMembership",
            group=group.descriptor,
            members=[user.descriptor]
        )
    
    def modify_project_permission(project: azuredevops.Project, group: azuredevops.Group):
        azuredevops.ProjectPermissions("projectPermissions",
            project_id=project.id,
            principal=group.id,
            permissions={
                "GENERIC_READ": "Allow"
            }
            )


    def modify_pipeline_permissions(project: azuredevops.Project, group: azuredevops.Group, pipeline: azuredevops.BuildDefinition, permissions: dict) -> None:
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
        azuredevops.BuildDefinitionPermissions("pipelinePermission",
            project_id=project.id,
            principal=group.id,
            build_definition_id=pipeline.id,
            permissions=permissions
            # link to doc page with permissions https://www.pulumi.com/registry/packages/azuredevops/api-docs/builddefinitionpermissions/
        )
        
