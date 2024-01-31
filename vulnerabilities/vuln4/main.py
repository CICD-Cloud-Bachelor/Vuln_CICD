import pulumi_azure as azure
from source.create_azure_devops import CreateAzureDevops
from source.container import DockerACR



def start(resource_group: azure.core.ResourceGroup):
    acr = DockerACR(resource_group, "registrypulumi")
    acr_string = acr.build_and_push_docker_image("mysqldb")
    connection_string = acr.start_container(acr_string, "mysql-container", 3306, 1.0, 1.0)
    
    github_repo_url = "https://github.com/CICD-Cloud-Bachelor/VULN4.git"
    azure_devops = CreateAzureDevops("VULN4", "Project for VULN4", "bachelor2024", resource_group)
    azure_devops.import_github_repo(github_repo_url, "VULN4_REPO")
    #azure_devops.create_work_item(40)
    azure_devops.add_variables({"CONNECTION_STRING": connection_string, "DATABASE": "prod", "USERNAME": "root", "PASSWORD": "myr00tp455w0rd"})
    azure_devops.create_ci_cd_pipeline("testpipeline")
    #azure_devops.run_pipeline("main")
