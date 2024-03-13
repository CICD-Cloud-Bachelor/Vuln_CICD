import pulumi
import pulumi_azuredevops as azuredevops
import pulumi_azure_native as azure_native
import pulumi_azure as azure
import os
from faker import Faker
from pulumi import Config
from pulumi_azuread import User as EntraUser
from source.users_groups import UserCreator, GroupCreator
from source.rest_test import *
import time
from source.config import *

fake = Faker()

class CreateAzureDevops:
    config = Config()
    def __init__(
            self, 
            project_name: str, 
            description: str, 
            organization_name: str, 
            resource_group: azure.core.ResourceGroup
        ) -> None:
        """
        Initializes an instance of CreateAzureDevops class.

        Args:
            project_name (str): The name of the Azure DevOps project.
            description (str): The description of the Azure DevOps project.
            organization_name (str): The name of the organization associated with the Azure DevOps project.
        """
        self.project_name = project_name
        self.description = description
        self.organization_name = organization_name
        self.project_url = f"https://dev.azure.com/{self.organization_name}/{self.project_name}"
        self.resource_group = resource_group
        self.entra_users = {}
        self.users = {}
        self.groups = {}
        self.variables = None
        self.__create_project()


    def __create_project(
            self
        ) -> None:
        """
        Creates an Azure DevOps project.
        """
        pulumi.log.info(f"Creating Azure DevOps project: {self.project_name}")
        self.project = azuredevops.Project(
            resource_name="project_" + os.urandom(5).hex(),
            name=self.project_name,
            description=self.description,
            features={
                "artifacts": "disabled",
                "testplans": "disabled",
            },
            visibility="private",
            work_item_template="Agile"  # Use the desired work item template
        )


    def import_github_repo(
            self, 
            github_repo_url: str, 
            repo_name: str
        ) -> None:
        """
        Imports a GitHub repository into the Azure DevOps project.

        Args:
            github_repo_url (str): The URL of the GitHub repository to import.
            repo_name (str): The name of the repository in Azure DevOps.
        """
        pulumi.log.info(f"Importing GitHub repository: {github_repo_url}")
        self.git_repo = azuredevops.Git(
            resource_name="gitRepo_" + os.urandom(5).hex(),
            name=repo_name,
            project_id=self.project.id,
            default_branch="refs/heads/main",
            initialization=azuredevops.GitInitializationArgs(
                init_type="Import",
                source_type="Git",
                source_url=github_repo_url
            )
        )
        pulumi.export("repository_web_url", self.git_repo.web_url)


    def create_pipeline(
        self, 
        name: str,
        run: bool,
        branch: str,
        variables: dict = None
        ) -> azuredevops.BuildDefinition:
        """
        Creates a CI/CD pipeline in Azure DevOps.

        Args:
            name (str): The name of the pipeline.
            run (bool): Indicates whether to run the pipeline after creation.
            branch (str): The branch to associate with the pipeline.
            variables (dict, optional): A dictionary of variables to add to the pipeline definition. 
                Each key-value pair represents a variable name and its corresponding value. 
                Defaults to None.

        Returns:
            azuredevops.BuildDefinition: The created CI/CD pipeline.

        """
        pulumi.log.info("Adding variables to pipeline definition")
        if variables is not None:    
            pipeline_variables = []
            for identifier, value in variables.items():
                pipeline_variables.append(
                    azuredevops.BuildDefinitionVariableArgs(
                        name=identifier,
                        secret_value=value,
                        is_secret=True,
                    )
                )

        pulumi.log.info("Creating CI/CD Pipeline")
        
        self.ci_cd_pipeline = azuredevops.BuildDefinition(
            resource_name=f"pipeline_{name}_" + os.urandom(5).hex(),
            project_id=self.project.id,
            name=name,
            repository=azuredevops.BuildDefinitionRepositoryArgs(
                repo_id=self.git_repo.id,
                repo_type="TfsGit",  # TfsGit corresponds to Azure Repos Git
                yml_path="azure-pipelines.yml"  # Path to your pipeline definition in your repo
            ),
            ci_trigger={
                "useYaml": True  # Enable continuous integration trigger using YAML
            },
            agent_pool_name="Azure Pipelines",
            variables=pipeline_variables or []
        )
        if run:
            pulumi.log.info(f"Running pipeline")
            RestWrapper(
                action_type="run_pipeline",
                inputs={
                    "project_name": self.project.name,
                    "pipeline_id": self.ci_cd_pipeline.id,
                    "branch": branch
                },
                opts=pulumi.ResourceOptions(depends_on=[self.ci_cd_pipeline, self.project])
            )

        return self.ci_cd_pipeline
    

    def __create_entra_user(
            self,
            name: str, 
            password: str
        ) -> EntraUser:
        """
        Creates a user in Entra (Azure AD).

        Args:
            name (str): The name of the user.
            password (str): The password for the user.

        Returns:
            EntraUser
        """
        login_name = f"{name.replace(' ', '.')}@{DOMAIN}"
        pulumi.log.info(f"Creating user in Entra (Azure AD) with login: {login_name}")
        
        entra_user = EntraUser(
            resource_name = name + "_" + os.urandom(5).hex(),
            display_name = name,
            user_principal_name = login_name,
            password = password,
            force_password_change = False # Set to True if you want to force a password change on first login
        )

        self.entra_users[name] = entra_user
        return entra_user
    

    def add_user(
                self,
                name: str, 
                password = None
            ) -> azuredevops.User:
            """
            Creates a user and adds it to the Azure DevOps instance.

            Args:
                name (str): The name of the user.
                password (str, optional): The password for the user. Defaults to None.

            Returns:
                azuredevops.User
            """
            if password is None:
                password = self.__random_password()

            entra_user = self.__create_entra_user(name, password)
            pulumi.log.info(f"Creating user in Azure DevOps: {name}")
            
            devops_user = azuredevops.User(
                resource_name = name + "_" + os.urandom(5).hex(),
                principal_name = entra_user.user_principal_name
            )

            self.users[name] = devops_user
            return devops_user
    
    def __random_password(self) -> str:
        return fake.password(length=10, special_chars=True, digits=True, upper_case=True, lower_case=True)
    

    def add_group(
                self,
                group_name: str
            ) -> azuredevops.Group:
            """
            Creates a group and adds it to the Azure Devops instance.

            Args:
                group_name (str): The name of the group to be added.

            Returns:
                azuredevops.Group
            """
            pulumi.log.info(f"Creating Azure DevOps group: {group_name}")
            devops_group = azuredevops.Group(f"customGroup_{group_name}_" + os.urandom(5).hex(),
                scope=self.project.id,
                display_name=group_name,
                description="Custom made permissions for devops"
            )

            self.groups[group_name] = devops_group
            return devops_group
    

    def add_user_to_group(
            self,
            user: azuredevops.User, 
            group: azuredevops.Group
        ) -> None:
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
    

    def modify_project_permissions(
            self,
            group: azuredevops.Group, 
            permissions: dict
        ) -> None:
        """
        Modifies the project permissions for a specific group.

        Args:
            group (azuredevops.Group): The group to modify permissions for.
            permissions (dict): The permissions to assign to the group.

        Returns:
            None
        """
        azuredevops.ProjectPermissions("projectPermissions_" + os.urandom(5).hex(),
            project_id=self.project.id,
            principal=group.id,
            permissions=permissions
        )
        # Link to permissions overview https://www.pulumi.com/registry/packages/azuredevops/api-docs/projectpermissions/
    

    def modify_repository_permissions(
            self,
            group: azuredevops.Group, 
            permissions: dict
        ) -> None:
        """
        Modifies the repository permissions for a specific group.

        Args:
            group (azuredevops.Group): The group to modify permissions for.
            permissions (dict): The permissions to assign to the group.

        Returns:
            None
        """
        pulumi.log.info("Modifying git repository permissions for group")
        azuredevops.GitPermissions("repositoryPermissions_" + os.urandom(5).hex(),
            project_id=self.project.id,
            principal=group.id,
            repository_id=self.git_repo.id,
            permissions=permissions
            # link to doc page with permissions https://www.pulumi.com/registry/packages/azuredevops/api-docs/gitpermissions/
        )


    def modify_pipeline_permissions(
            self,
            group: azuredevops.Group, 
            permissions: dict
        ) -> None:
        """
        Modifies the pipeline permissions for a specific group.

        Args:
            group (azuredevops.Group): The group to modify permissions for.
            permissions (dict): The permissions to assign to the group.

        Returns:
            None
        """
        pulumi.log.info("Modifying pipeline permissions for group")
        azuredevops.BuildDefinitionPermissions("pipelinePermissions_" + os.urandom(5).hex(),
            project_id=self.project.id,
            principal=group.id,
            build_definition_id=self.ci_cd_pipeline.id,
            permissions=permissions
            # link to doc page with permissions https://www.pulumi.com/registry/packages/azuredevops/api-docs/builddefinitionpermissions/
        )
    

    def modify_branch_permissions(
            self,
            group: azuredevops.Group,
            branch: str,
            permissions: dict
        ) -> None:
        """
        Modifies the branch permissions for a specific group.

        Args:
            group (azuredevops.Group): The group to modify permissions for.
            branch (str): The name of the branch.
            permissions (dict): The permissions to assign to the group.

        Returns:
            None
        """
        pulumi.log.info("Modifying git branch permissions for group")
        azuredevops.GitPermissions("branchPermissions_" + os.urandom(5).hex(),
            project_id=self.project.id,
            principal=group.id,
            repository_id=self.git_repo.id,
            branch_name=branch,
            permissions=permissions
            # link to doc page with permissions https://www.pulumi.com/registry/packages/azuredevops/api-docs/gitpermissions/
        )
    

    def create_work_item(
            self,
            type: str,
            title: str,
            assigned_to: str,
            description: str,
            comments: list[str],
            depends_on: list = []
        ) -> None:
        pulumi.log.info(f"Creating work item")
        RestWrapper(
            action_type="create_work_item",
            inputs={
                "project_name": self.project.name,
                "title": title,
                "assigned_to": assigned_to,
                "description": description,
                "type": type,
                "comments": comments
            },
            opts=pulumi.ResourceOptions(depends_on=depends_on)
        )


    def create_wiki(
            self,
            wiki_name: str
        ) -> None:
        pulumi.log.info(f"Creating wiki")
        RestWrapper(
            action_type="create_wiki",
            inputs={
                "wiki_name": wiki_name,
                "project_id": self.project.id
            },
            opts=pulumi.ResourceOptions(depends_on=[self.project])
        )
    

    def create_wiki_page(
            self,
            wiki_name: str,
            page_name: str,
            page_content: str
        ) -> None:
        pulumi.log.info(f"Creating wiki page")
        RestWrapper(
            action_type="create_wiki_page",
            inputs={
                "project_id": self.project.id,
                "wiki_name": wiki_name,
                "page_name": page_name,
                "page_content": page_content
            },
            opts=pulumi.ResourceOptions(depends_on=[self.project])
        )