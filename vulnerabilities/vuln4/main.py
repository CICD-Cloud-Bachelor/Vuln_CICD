import pulumi_azure as azure
import pulumi_azuredevops as azuredevops
from source.create_azure_devops import CreateAzureDevops
from source.container import DockerACR
from source.workitem import WorkItem
from source.users_groups import GroupCreator, UserCreator
import configparser
from faker import Faker


faker = Faker()
config = configparser.ConfigParser()
config.read('config.ini')
ORGANIZATION_NAME = config["AZURE"]["ORGANIZATION_NAME"]
REGISTRY_NAME = config["DOCKER"]["REGISTRY_NAME"]

PROJECT_NAME = "VULN4"
PROJECT_DESCRIPTION = "Project for VULN4"
GITHUB_REPO_URL = "https://github.com/CICD-Cloud-Bachelor/VULN4.git"
REPO_NAME = "VULN4_REPO"
PIPELINE_NAME = "testpipeline"
IMAGE_NAME = "mysqldb"
CONTAINER_NAME = "mysql-container"



def start(resource_group: azure.core.ResourceGroup):
    acr = DockerACR(
        resource_group=resource_group, 
        registry_name=REGISTRY_NAME
    )
    
    acr_string = acr.build_and_push_docker_image(
        image_name=IMAGE_NAME
    )

    connection_string = acr.start_container(
        docker_acr_image_name=acr_string, 
        container_name=CONTAINER_NAME, 
        ports=[3306], 
        cpu=1.0, 
        memory=1.0
    )
    import pulumi
    pulumi.export("connection_string", connection_string)   
    
    # azure_devops = CreateAzureDevops(
    #     project_name=PROJECT_NAME, 
    #     description=PROJECT_DESCRIPTION, 
    #     organization_name=ORGANIZATION_NAME, 
    #     resource_group=resource_group
    # )

    # azure_devops.create_wiki(
    #     wiki_name="VULN4_WIKI"
    # )

    # azure_devops.create_wiki_page(
    #     wiki_name="VULN4_WIKI",
    #     page_content="This is a test page",
    #     page_name="TestPage"
    # )
    # azure_devops.create_wiki_page(
    #     wiki_name="VULN4_WIKI",
    #     page_content="New page",
    #     page_name="Info"
    # )

    # azure_devops.import_github_repo(
    #     github_repo_url=GITHUB_REPO_URL, 
    #     repo_name=REPO_NAME
    # )
    # azure_devops.add_variables(
    #     {
    #         "CONNECTION_STRING": "a",#connection_string, 
    #         "DATABASE": "prod", 
    #         "USERNAME": "root", 
    #         "PASSWORD": "myr00tp455w0rd"
    #     }
    # )
    # pipeline = azure_devops.create_ci_cd_pipeline(
    #     name=PIPELINE_NAME
    # )

    # azure_devops.run_pipeline(
    #     branch="main"
    # )

    # devops_group = GroupCreator.create_group(
    #     project=azure_devops.project, 
    #     group_name="Custom Group"
    # )
    # devops_user = UserCreator.create_devops_user(
    #     name="TOMMEN tomm",#faker.name().replace(".", " "),
    #     password="Troll57Hoho69%MerryChristmas"
    # )
    # GroupCreator.add_user_to_group(devops_user, devops_group)

    # users = [
    #     UserCreator.create_devops_user(
    #         name=faker.name().replace(".", ""),
    #         password=UserCreator.randomPass()
    #     ) for _ in range(3)
    # ]

    # for user in users:
    #     GroupCreator.add_user_to_group(user, devops_group)

    # GroupCreator.modify_project_permission(
    #     project=azure_devops.project, 
    #     group=devops_group, 
    #     permissions={
    #         "GENERIC_READ": "Allow",
    #     }
    # )
    # GroupCreator.modify_pipeline_permissions(
    #     project=azure_devops.project, 
    #     group=devops_group, 
    #     pipeline=pipeline, 
    #     permissions={
    #         "ViewBuilds": "Allow",
    #         "ViewBuildDefinition": "Allow"
    #     }
    # )
    # GroupCreator.modify_repository_permissions(
    #     project=azure_devops.project, 
    #     group=devops_group, 
    #     repository=azure_devops.git_repo,
    #     permissions={
    #         "GenericRead": "Allow"
    #     }
    # ) 
    # GroupCreator.modify_area_permissions(
    #     project=azure_devops.project, 
    #     group=devops_group, 
    #     permissions={
    #         "GENERIC_READ": "Allow",
    #         "WORK_ITEM_READ": "Allow",
    #     }
    # )
    # azure_devops.create_work_item(
    #     type="Task",
    #     title="Investigate production outage",
    #     description="Investigate production outage",
    #     assigned_to=devops_user.principal_name,
    #     comments=[
    #         "Correct", 
    #         "Investigate production outage", 
    #         "Investigate", 
    #         "Fix production outage"
    #     ],
    #     depends_on=[devops_user, azure_devops.project]
    # )
  