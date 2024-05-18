import pulumi
import pulumi_azuredevops as azuredevops
import pulumi_azure_native as azure_native
import pulumi_azure as azure
import os
from faker import Faker
import json
import random
from pulumi import Config
from pulumi_azuread import User as EntraUser
from source.azure_devops_rest_api import *
from source.config import *

fake = Faker()

class CreateAzureDevops:
    """
    Automates the creation and management of Azure DevOps projects, repositories, and users.
    """
    config = Config()
    def __init__(
            self, 
            project_name: str, 
            description: str, 
            organization_name: str, 
            resource_group: azure.core.ResourceGroup
        ) -> None:
        """
        Initializes an instance of CreateAzureDevops, setting up a new project and preparing the environment.

        Args:
            project_name (str): Name of the Azure DevOps project to create.
            description (str): Description of the Azure DevOps project.
            organization_name (str): Azure DevOps organization name under which the project will be created.
            resource_group (azure.core.ResourceGroup): Resource group where the resources will be allocated.

        Example:
            >>> devops_creator = CreateAzureDevops("ExampleProject", "An example project.", "ExampleOrg", resource_group)
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
        self.has_called_workitem = False
        self.__create_project()

    def __create_project(
            self
        ) -> None:
        """
        Private method to create a new Azure DevOps project using the Pulumi Azure DevOps provider.

        Example:
            >>> self.__create_project()
        """
        pulumi.log.info(f"Creating Azure DevOps project: {self.project_name}")
        self.project = azuredevops.Project(
            resource_name=f"project{os.urandom(5).hex()}",
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
            repo_name: str,
            is_private: bool,
            pat: str = None
        ) -> None:
        """
        Imports a GitHub repository into the newly created Azure DevOps project.

        Args:
            github_repo_url (str): URL of the GitHub repository to import.
            repo_name (str): Name for the repository in Azure DevOps.
            is_private (bool): Flag indicating if the GitHub repository is private.
            pat (str, optional): Personal Access Token used if the repository is private.

        Example:
            >>> devops_creator.import_github_repo("https://github.com/example/repo", "ExampleRepo", True, "your_pat_here")
        """
        github_service_endpoint = None

        # Private repo does not work btw, idk why
        # Tried both using the PAT in the beginning of the link and creating a pulumi GithubServiceConnection object
        # Could not get it to work
        if is_private:
            github_repo_url = github_repo_url.replace("https://", f"https://{pat}@")

        pulumi.log.info(f"Importing GitHub repository: {github_repo_url}")
        self.git_repo = azuredevops.Git(
            resource_name="gitRepo_" + os.urandom(5).hex(),
            name=repo_name,
            project_id=self.project.id,
            default_branch="refs/heads/main",
            initialization=azuredevops.GitInitializationArgs(
                init_type="Import",
                source_type="Git",
                source_url=github_repo_url,
            )
        )


    def create_pipeline(
        self, 
        name: str,
        run: bool,
        branch: str,
        variables: dict = None
        ) -> azuredevops.BuildDefinition:
        """
        Creates a new CI/CD pipeline in the Azure DevOps project.

        Args:
            name (str): Name of the pipeline.
            run (bool): Whether to run the pipeline immediately after creation.
            branch (str): The repository branch that the pipeline will target.
            variables (dict, optional): Variables to be used in the pipeline configuration.

        Returns:
            azuredevops.BuildDefinition: The newly created pipeline object.

        Example:
            >>> pipeline = devops_creator.create_pipeline("DeployPipeline", True, "main", {"BuildConfig": "Release"})
        """
        pipeline_variables = None
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
    
    @staticmethod
    def create_entra_user(
            name: str, 
            password: str = None
        ) -> EntraUser:
        """
        Creates a new user in Azure Active Directory (Entra).

        Args:
            name (str): The full name of the user.
            password (str, optional): The password for the new user. If not provided, a random password is generated.

        Returns:
            EntraUser: The created Azure AD user.

        Example:
            >>> entra_user = devops_creator.create_entra_user("John Doe", "SecurePass123!")
        """
        if password is None:
                password = CreateAzureDevops.random_password()

        login_name = f"{name.replace(' ', '.')}@{DOMAIN}"
        pulumi.log.info(f"Creating user in Entra (Azure AD) with login: {login_name}")
        
        entra_user = EntraUser(
            resource_name = name + "_" + os.urandom(5).hex(),
            display_name = name,
            user_principal_name = login_name,
            password = password,
            force_password_change = False # Set to True if you want to force a password change on first login
        )

        return entra_user
    

    def add_user(
                self,
                name: str, 
                password: str = None
            ) -> azuredevops.User:
            """
            Creates a new user in Azure DevOps and links it to a newly created Azure AD user.

            Args:
                name (str): The full name of the user.
                password (str, optional): The password for the new user. If not provided, a random password is generated.

            Returns:
                azuredevops.User: The created Azure DevOps user.

            Example:
                >>> devops_user = devops_creator.add_user("Jane Doe", "SecurePass123!")
            """

            entra_user = CreateAzureDevops.create_entra_user(name, password)
            pulumi.log.info(f"Creating user in Azure DevOps: {name}")
            
            devops_user = azuredevops.User(
                resource_name = name + "_" + os.urandom(5).hex(),
                principal_name = entra_user.user_principal_name,
                opts=pulumi.ResourceOptions(depends_on=[entra_user])
            )

            self.users[name] = devops_user
            return devops_user
    
    def add_entra_user_to_devops(user: dict) -> azuredevops.User:
        """
        Creates a new user in Azure DevOps and links it to an existing Azure AD user.

        Args:
            user (dict): A dictionary containing the full name and Azure AD user object.

        Returns:
            azuredevops.User: The created Azure DevOps user.
        
        Example:
            >>> devops_user = devops_creator.add_entra_user_to_devops({"username": "Jane Doe", "entra_user": entra_user})
        """
        pulumi.log.info(f"Creating user in Azure DevOps: {user['username']}")
        devops_user = azuredevops.User(
            resource_name = user["username"] + "_" + os.urandom(5).hex(),
            principal_name = user["entra_user"].user_principal_name,
            opts=pulumi.ResourceOptions(depends_on=[user["entra_user"]])
        )
        return devops_user
    
    def random_password() -> str:
        """
        Generates a random password using the Faker library.

        Returns:
            str: A randomly generated password.
        
        Example:
            >>> password = CreateAzureDevops.random_password()
        """
        return fake.password(length=10, special_chars=True, digits=True, upper_case=True, lower_case=True)
    

    def add_group(
                self,
                group_name: str
            ) -> azuredevops.Group:
            """
            Creates a new group in Azure DevOps.

            Args:
                group_name (str): The name of the group to create.

            Returns:
                azuredevops.Group: The newly created group.

            Example:
                >>> group = devops_creator.add_group("Developers")
            """
            pulumi.log.info(f"Creating Azure DevOps group: {group_name}")
            devops_group = azuredevops.Group(f"customGroup_{group_name}_" + os.urandom(5).hex(),
                scope=self.project.id,
                display_name=group_name,
                description="Custom made permissions for devops"
            )

            self.groups[group_name] = devops_group
            return devops_group
    
    def add_user_to_default_group(
            self,
            user: azuredevops.User,
            default_group_name: str
        ) -> None:
        """
        Adds an Azure DevOps user to a default group by fetching the group's descriptor from Azure DevOps and creating a membership.

        Args:
            user (azuredevops.User): The user to add to the group.
            default_group_name (str): The name of the default group to add the user to.

        Example:
            >>> user = devops_creator.add_user("Jane Doe")
            >>> devops_creator.add_user_to_default_group(user, "Contributors")
        """
        pulumi.log.info(f"Adding user to default group: {default_group_name}")

        default_group = azuredevops.get_group_output(
            project_id=self.project.id,
            name=default_group_name
        )

        azuredevops.GroupMembership("groupMembership_" + os.urandom(5).hex(),
            group=default_group.descriptor,
            members=[user.descriptor]
        )
        
    def add_user_to_group(
            self,
            user: azuredevops.User, 
            group: azuredevops.Group
        ) -> None:
        """
        Adds a user to a group in Azure DevOps.

        Args:
            user (azuredevops.User): The user to add to the group.
            group (azuredevops.Group): The group to which the user will be added.

        Example:
            >>> devops_user = devops_creator.add_user("Jane Doe")
            >>> group = devops_creator.add_group("Developers")
            >>> devops_creator.add_user_to_group(devops_user, group)
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
        Modifies permissions for a specific group within a project in Azure DevOps.

        Args:
            group (azuredevops.Group): The group whose permissions will be modified.
            permissions (dict): A dictionary defining the permissions to set.

        Example:
            >>> group = devops_creator.add_group("Developers")
            >>> permissions = {"GENERIC_READ": "Allow", "GENERIC_WRITE": "Allow"}
            >>> devops_creator.modify_project_permissions(group, permissions)
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
        Modifies permissions for a specific repository for a group in Azure DevOps.

        Args:
            group (azuredevops.Group): The group whose repository permissions will be modified.
            permissions (dict): A dictionary defining the repository permissions to set.

        Example:
            >>> group = devops_creator.add_group("Developers")
            >>> permissions = {"GENERIC_READ": "Allow", "GENERIC_WRITE": "Allow"}
            >>> devops_creator.modify_repository_permissions(group, permissions)
        """
        pulumi.log.info("Modifying git repository permissions for group")
        azuredevops.GitPermissions("repositoryPermissions_" + os.urandom(5).hex(),
            project_id=self.project.id,
            principal=group.id,
            repository_id=self.git_repo.id,
            permissions=permissions
            # link to doc page with permissions https://www.pulumi.com/registry/packages/azuredevops/api-docs/gitpermissions/
        )

    def modify_area_permissions(
        self,
        group: azuredevops.Group,
        permissions: dict
        ) -> None:
        """
        Modifies the area permissions for a specific group in Azure DevOps.

        Args:
            group (azuredevops.Group): The group to which the permissions will be applied.
            permissions (dict): A dictionary of permissions to apply.

        Example:
            >>> group = devops_creator.add_group("QA Team")
            >>> permissions = {"GENERIC_READ": "Allow", "GENERIC_WRITE": "Allow"}
            >>> devops_creator.modify_area_permissions(group, permissions)
        """
        pulumi.log.info("Modifying area permissions for group")
        azuredevops.AreaPermissions("areaPermissions_" + os.urandom(5).hex(),
            project_id=self.project.id,
            principal=group.id,
            path="/",
            permissions=permissions
            # link to doc page with permissions https://www.pulumi.com/registry/packages/azuredevops/api-docs/areapermissions/
        )

    def modify_pipeline_permissions(
            self,
            group: azuredevops.Group, 
            permissions: dict
        ) -> None:
        """
        Modifies the pipeline permissions for a specific group in Azure DevOps.

        Args:
            group (azuredevops.Group): The group to which the pipeline permissions will be applied.
            permissions (dict): A dictionary of permissions to set for the pipeline.

        Example:
            >>> group = devops_creator.add_group("DevOps Team")
            >>> permissions = {"ViewBuilds": "Allow", "ViewBuildDefinition": "Deny"}
            >>> devops_creator.modify_pipeline_permissions(group, permissions)
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
        Modifies permissions for a specific branch for a group in Azure DevOps.

        Args:
            group (azuredevops.Group): The group whose branch permissions will be modified.
            branch (str): The branch to which permissions will be applied.
            permissions (dict): The permissions settings to apply.

        Example:
            >>> group = devops_creator.add_group("Feature Team")
            >>> permissions = {"EditBranch": "Allow", "DeleteBranch": "Deny"}
            >>> devops_creator.modify_branch_permissions(group, "develop", permissions)
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
    
    
    def generate_random_work_items(
            self,
            assigned_to: str,
            amount: int,
        ) -> None:
        """
        Generates a specified number of random work items for project management purposes.

        Args:
            assigned_to (str): The Azure DevOps username to which the work items will be assigned.
            amount (int): The number of work items to generate.

        Example:
            >>> devops_creator.generate_random_work_items("john.doe@example.com", 5)
        """
        pulumi.log.info(f"Generating random work items")

        with open("templates/work_items/work_item_dataset.json", "r") as file:
            work_item_dataset = json.load(file)
        
        templates = work_item_dataset["templates"]
        service_names = work_item_dataset["service_names"]
        resource_names = work_item_dataset["resource_names"]
        user_roles = work_item_dataset["user_roles"]

        for i in range(amount):
            title, description = self.generate_fake_text(templates, service_names, resource_names, user_roles)
            type = random.choice(["Task", "Bug", "Feature", "Epic", "Issue"])
            state = random.choice(["New", "Active", "Closed"])

            comment = ["Work item has been closed as this has been resolved."] if state == "Closed" else []

            RestWrapper(
                action_type="create_work_item",
                inputs={
                    "project_name": self.project.name,
                    "title": title,
                    "assigned_to": assigned_to,
                    "description": description,
                    "type": type,
                    "state": state,
                    "comments": comment
                },
            )

    def create_work_item(
            self,
            type: str,
            title: str,
            assigned_to: str,
            description: str,
            comments: list[str],
            state: str = "New",
            depends_on: list = []
        ) -> None:
        """
        Creates a new work item in Azure DevOps with specified details.

        Args:
            type (str): The type of work item (e.g., "Task", "Bug").
            title (str): The title of the work item.
            assigned_to (str): The username to which the work item will be assigned.
            description (str): A brief description of the work item.
            comments (list[str]): A list of comments to be added to the work item.
            state (str, optional): The initial state of the work item ("New" by default).
            depends_on (list, optional): A list of Pulumi resources that this operation depends on.

        Example:
            >>> devops_creator.create_work_item("Bug", "Login Failure", "jane.doe@example.com", "Users cannot log in.", ["Urgent issue reported by several users."], "Active")
        """
        pulumi.log.info(f"Creating work item")

        RestWrapper(
            action_type="create_work_item",
            inputs={
                "project_name": self.project.name,
                "title": title,
                "assigned_to": assigned_to,
                "description": description,
                "type": type,
                "comments": comments,
                "state": state
            },
            opts=pulumi.ResourceOptions(depends_on=[self.project]+depends_on)
        )

    def create_wiki_with_content(
            self,
            wiki_name: str,
            page_name: str,
            markdown_file_path: str
        ) -> None:
        """
        Creates a wiki page in Azure DevOps from a markdown file.

        Args:
            wiki_name (str): The name of the wiki to create or update.
            page_name (str): The name of the new wiki page.
            markdown_file_path (str): The path to the markdown file containing the page content.

        Example:
            >>> devops_creator.create_wiki_with_content("ProjectWiki", "HomePage", "./docs/HomePage.md")
        """

        pulumi.log.info(f"Creating wiki")

        with open(markdown_file_path, "r") as markdown_file:
            page_content = markdown_file.read()

        RestWrapper(
            action_type="create_wiki_with_content",
            inputs={
                "project_id": self.project.id,
                "wiki_name": wiki_name,
                "page_name": page_name,
                "page_content": page_content
            },
            opts=pulumi.ResourceOptions(depends_on=[self.project])
        )
    
    def generate_fake_text(
            self,
            templates: list[str],
            service_names: list[str],
            resource_names: list[str],
            user_roles: list[str]
    ):
        """
        Generates fake title and description text for work items using provided templates and random elements from service names, resource names, and user roles.

        Args:
            templates (list[str]): List of template strings that include placeholders for service names, resource names, and user roles.
            service_names (list[str]): List of potential service names to insert into templates.
            resource_names (list[str]): List of potential resource names to insert into templates.
            user_roles (list[str]): List of potential user roles to insert into templates.

        Returns:
            tuple: A tuple containing a randomly generated title and description.

        Example:
            >>> title, description = devops_creator.generate_fake_text(
                    ["Fix {service_name}", "Update {resource_name}", "Review {user_role} permissions"],
                    ["API Gateway", "Database", "Load Balancer"],
                    ["Resource Group A", "Storage Account B", "Virtual Network C"],
                    ["Administrator", "Developer", "Analyst"]
                )
            >>> print(title, description)
        """
        random_template = random.choice(templates)
        title = random_template["title"]
        template_text = random_template["template"]

        generate_text = template_text.format(
            service_name=random.choice(service_names),
            resource_name=random.choice(resource_names),
            user_role=random.choice(user_roles)
        )
        return title, generate_text
        