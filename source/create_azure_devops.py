import pulumi
import pulumi_azuredevops as azuredevops
import pulumi_azure_native as azure_native
import pulumi_azure as azure
import os
import json
from pulumi import Config
from source.users_groups import UserCreator, GroupCreator
from source.rest_test import *
import configparser, time

config = configparser.ConfigParser()
config.read('config.ini')
ORGANIZATION_NAME = config["AZURE"]["ORGANIZATION_NAME"]
PAT = config["AZURE"]["PAT"]
USERNAME = config["AZURE"]["USERNAME"]
DOMAIN = config["AZURE"]["DOMAIN"]

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
        self.users = {}
        self.groups = {}
        self.variables = None
        self.has_called_workitem = False
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

    def create_ci_cd_pipeline(
            self, 
            name: str
        ) -> azuredevops.BuildDefinition:
        """
        Creates a CI/CD pipeline in Azure DevOps.

        Args:
            name (str): The name of the CI/CD pipeline.
        """
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
            variables=self.variables or []
        )
        return self.ci_cd_pipeline
        

    def run_pipeline(
            self, 
            branch: str
        ) -> None:
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

    def add_variables(
            self, 
            variables: dict
        ) -> None:
        self.variables = []
        for identifier, value in variables.items():
            self.variables.append(
                azuredevops.BuildDefinitionVariableArgs(
                    name=identifier,
                    secret_value=value,
                    is_secret=True,
                )
            )

    def add_user(
                self,
                name: str, 
                password = None
            ) -> None:
            """
            Creates a user and adds it to the Azure DevOps instance.

            Args:
                name (str): The name of the user.
                password (str, optional): The password for the user. Defaults to None.

            Returns:
                None
            """

            devops_user = UserCreator.create_devops_user(
                name, 
                password
            )
            self.users[name] = devops_user
    
    def add_group(
                self,
                group_name: str
            ) -> None:
            """
            Creates a group and adds it to the Azure Devops instance.

            Args:
                group_name (str): The name of the group to be added.

            Returns:
                None
            """

            custom_group = GroupCreator.create_group(
                self.project, 
                group_name
            )
            self.groups[group_name] = custom_group
    
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
        GroupCreator.add_user_to_group(
            user, 
            group
        )
    
    def modify_project_permission(
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
        GroupCreator.modify_project_permission(
            self.project, 
            group,
            permissions
        )
    
    def modify_repo_permission(
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
        GroupCreator.modify_repository_permissions(
            self.project,
            group,
            self.git_repo,
            permissions
        )

    def modify_pipeline_permission(
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
        GroupCreator.modify_pipeline_permissions(
            self.project,
            group,
            self.ci_cd_pipeline,
            permissions
        )
    
    def modify_branch_permission(
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
        GroupCreator.modify_branch_permissions(
            self.project,
            group,
            self.git_repo,
            branch,
            permissions
        )
    
    def modify_area_permission(
            self,
            group: azuredevops.Group,
            permissions: dict
        ) -> None:
        """
        Modifies the area permissions for a specific group.

        Args:
            group (azuredevops.Group): The group to modify permissions for.
            permissions (dict): The permissions to assign to the group.

        Returns:
            None
        """
        GroupCreator.modify_area_permissions(
            self.project,
            group,
            permissions
        )
    
    def generate_random_work_items(
            self,
            assigned_to: str,
            amount: int,
        ) -> None:
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
                opts=pulumi.ResourceOptions(depends_on=[self.project])
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
            markdown_file_path: str
        ) -> None:
        pulumi.log.info(f"Creating wiki page")

        with open(markdown_file_path, "r") as markdown_file:
            page_content = markdown_file.read()

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
    
    def generate_fake_text(
            self,
            templates: list[str],
            service_names: list[str],
            resource_names: list[str],
            user_roles: list[str]
    ) -> str:
        """
        Generates fake text using a random template.

        Args:
            templates (list[str]): A list of templates to choose from.
            service_names (list[str]): A list of service names to use in the generated text.
            resource_names (list[str]): A list of resource names to use in the generated text.
            user_roles (list[str]): A list of user roles to use in the generated text.

        Returns:
            str: The generated fake text.
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
        