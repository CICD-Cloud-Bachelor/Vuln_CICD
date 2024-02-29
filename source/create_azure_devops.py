import pulumi
import pulumi_azuredevops as azuredevops
import pulumi_azure_native as azure_native
import pulumi_azure as azure
import os
from pulumi import Config
<<<<<<< HEAD
from source.azure_devops_rest_api import AzureDevOpsPipelineRun, AzureDevOpsPipelineRunProvider
import configparser
import random
=======
from source.rest_test import *
import configparser, time
>>>>>>> Dev

config = configparser.ConfigParser()
config.read('config.ini')
ORGANIZATION_NAME = config["AZURE"]["ORGANIZATION_NAME"]
PAT = config["AZURE"]["PAT"]
USERNAME = config["AZURE"]["USERNAME"]

class CreateAzureDevops:
    config = Config()
    def __init__(self, 
            project_name: str, 
            description: str, 
            organization_name: str, 
            resource_group: azure.core.ResourceGroup) -> None:
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
        self.variables = None
        self.__create_project()


    def __create_project(
            self
        ) -> None:
        """
        Creates an Azure DevOps project.
        """
        pulumi.log.info(f"Creating Azure DevOps project: {self.project_name}")
        self.project = azuredevops.Project("project_" + os.urandom(5).hex(),
            name=self.project_name,
            description=self.description,
            features={
                "artifacts": "disabled",
                "testplans": "disabled",
            },
            visibility="private",
            work_item_template="Agile"  # Use the desired work item template
        )


    def import_github_repo(self, 
            github_repo_url: str, 
            repo_name: str) -> None:
        """
        Imports a GitHub repository into the Azure DevOps project.

        Args:
            github_repo_url (str): The URL of the GitHub repository to import.
            repo_name (str): The name of the repository in Azure DevOps.
        """
        pulumi.log.info(f"Importing GitHub repository: {github_repo_url}")
        self.git_repo = azuredevops.Git("gitRepo_" + os.urandom(5).hex(),
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

    def create_ci_cd_pipeline(self, 
            name: str) -> azuredevops.BuildDefinition:
        """
        Creates a CI/CD pipeline in Azure DevOps.

        Args:
            name (str): The name of the CI/CD pipeline.
        """
        pulumi.log.info(f"Creating CI/CD Pipeline")
        
        self.ci_cd_pipeline = azuredevops.BuildDefinition("ci-pipeline",
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

    def create_work_item(
            self, 
            count: int
        ) -> None:
        pulumi.log.info(f"Creating {count} work items")

        for _ in range(count):
            # Work item details
            # Randomly select a work item type from the predefined list
            self.work_item_type = random.choice(["Epic", "Feature", "User Story", "Bug"])

            # Randomly select a work item title based on the work item type
            self.work_item_title = random.choice([
                "Investigate production outage",
                "Add new feature",
                "Update documentation",
                "Refactor code",
                "Fix bug",
                "Add tests",
                "Update dependencies",
                "Add new endpoint"
            ]) 
           
            self.work_item_state = "New" 

            # Create a new Azure DevOps work item in the provided project
            work_item = azuredevops.Workitem("workItem_" + self.work_item_title + str(random.randint(1, 100000)),
                project_id=self.project.id,
                type=self.work_item_type,
                title=self.work_item_title,
                state=self.work_item_state
            )
            
            pulumi.export("work_item_id", work_item.id)

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