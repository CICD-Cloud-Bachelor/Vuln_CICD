import pulumi_azure as azure
from source.add_users import CreateUsers
from source.create_azure_devops import CreateAzureDevops
from source.container import CreateContainer, DockerACR



def start(resource_group: azure.core.ResourceGroup):
    acr = DockerACR(resource_group, "registrypulumi")
    acr_string = acr.build_and_push_docker_image("mysqldb")
    acr.start_container(acr_string, "mysql-container", 3306, 1.0, 1.0)
    
    github_repo_url = "https://github.com/CICD-Cloud-Bachelor/VULN4.git"
    azure_devops = CreateAzureDevops("testproject", "This is a test project.", "bachelor2024", resource_group)
    azure_devops.import_github_repo(github_repo_url, "testrepo")
    azure_devops.create_work_item(40)
    azure_devops.create_ci_cd_pipeline("testpipeline")
    azure_devops.run_pipeline("main")
