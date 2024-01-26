"""A Python Pulumi program"""
import pulumi_azure as azure
import add_users
import container
from create_azure_devops import CreateAzureDevops

resource_group = azure.core.ResourceGroup('resource-group', location="West Europe")

github_repo_url = "https://github.com/Oslolosen/bachelor_docs.git"

azure_devops = CreateAzureDevops("testproject", "This is a test project.", "bachelor2024", resource_group)
azure_devops.import_github_repo(github_repo_url, "testrepo")
#azure_devops.create_work_item(2)
azure_devops.add_flag_pipeline_secret("flag1", "FLAG{testflag}")
azure_devops.create_ci_cd_pipeline("testpipeline")