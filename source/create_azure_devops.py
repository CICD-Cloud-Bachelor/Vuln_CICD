import pulumi
import pulumi_azuredevops as azuredevops
import pulumi_azure_native as azure_native
import pulumi_azure as azure
import os
from pulumi import Config
from source.users_groups import UserCreator, GroupCreator
from source.azure_devops_rest_api import AzureDevOpsPipelineRun, AzureDevOpsPipelineRunProvider
import configparser

config = configparser.ConfigParser()
config.read('config.ini')
ORGANIZATION_NAME = config["AZURE"]["ORGANIZATION_NAME"]
PAT = config["AZURE"]["PAT"]
USERNAME = config["AZURE"]["USERNAME"]

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
        pulumi.log.info(f"Pushing to git and starting pipeline")
        AzureDevOpsPipelineRun(
            name="myPipelineRun",
            organization=ORGANIZATION_NAME,
            username=USERNAME,
            project=self.project,
            personal_access_token=PAT,
            pipeline_id=self.ci_cd_pipeline.id,
            source_branch=branch,
            opts=pulumi.ResourceOptions(parent=self.ci_cd_pipeline)
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
        

