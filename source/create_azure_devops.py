import pulumi
import pulumi_azuredevops as azuredevops
import pulumi_azure_native as azure_native
import pulumi_azure as azure
from pulumi import Config
import requests
import random
import base64



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
        self.variables = None
        self.__create_project()


    def __create_project(
            self
        ) -> None:
        """
        Creates an Azure DevOps project.
        """
        pulumi.log.info(f"Creating Azure DevOps project: {self.project_name}")
        self.project = azuredevops.Project("project",
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
        self.git_repo = azuredevops.Git("gitRepo",
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
        pulumi.log.info(f"Creating CI/CD Pipeline")
        
        ci_cd_pipeline = azuredevops.BuildDefinition("ci-pipeline",
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
        return ci_cd_pipeline
        

    def run_pipeline(
            self, 
            branch: str
        ) -> None:
        pulumi.log.info(f"Pushing to git and starting pipeline")
        azuredevops.GitRepositoryFile(
            "new-file",
            repository_id=self.git_repo.id,
            file=".ignoreme",
            content="Ignore me, this file is only here to trigger a pipeline run",
            commit_message="Add .ignoreme",
            branch=f"refs/heads/{branch}"
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




        

