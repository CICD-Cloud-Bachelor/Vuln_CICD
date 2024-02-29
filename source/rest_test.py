from pulumi.dynamic import Resource, ResourceProvider, CreateResult
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from azure.devops.v7_1.work_item_tracking.models import CommentCreate
from azure.devops.v7_1.wiki.models import WikiCreateParametersV2
from azure.devops.v7_1.wiki.models import WikiPageCreateOrUpdateParameters
import configparser, random, time

config = configparser.ConfigParser()
config.read('config.ini')

USERNAME = config["AZURE"]["USERNAME"]
PAT = config["AZURE"]["PAT"]
ORGANIZATION_NAME = config["AZURE"]["ORGANIZATION_NAME"]


class RestAPI(ResourceProvider):
    def create(self, inputs: dict) -> CreateResult:
        credentials = BasicAuthentication(
            username=USERNAME, 
            password=PAT
        )
        self.connection = Connection(
            base_url=f"https://dev.azure.com/{ORGANIZATION_NAME}/",
            creds=credentials
        )
        action_type = inputs.get("action_type")
        
        if action_type == "run_pipeline":
            return self.run_pipeline(inputs)
        elif action_type == "create_work_item":
            return self.create_work_item(inputs)
        elif action_type == "create_wiki":
            return self.create_wiki(inputs)
        elif action_type == "create_wiki_page":
            return self.create_wiki_page(inputs)
        else:
            raise Exception("Invalid action type")

    def run_pipeline(
            self,
            inputs: dict
        ) -> CreateResult:
        pipelines_client = self.connection.clients.get_pipelines_client()

        run = pipelines_client.run_pipeline(
            run_parameters={
                "resources": 
                {
                    "repositories": 
                    {
                        "self": 
                        {
                            "refName": f"refs/heads/{inputs.get('branch')}"
                        }
                    }
                }
            }, 
            project=inputs.get("project_name"), 
            pipeline_id=inputs.get("pipeline_id")
        )
        return CreateResult(id_="1", outs={"run id": run.id})

    def create_work_item(
            self,
            inputs: dict
        ) -> CreateResult:
        work_item_client = self.connection.clients.get_work_item_tracking_client()

        fields = {
            "/fields/System.Title": inputs.get("title"),
            "/fields/System.AssignedTo": inputs.get("assigned_to"),
            "/fields/System.Description": inputs.get("description")
        }
        time.sleep(60)
        work_item = work_item_client.create_work_item(
            document = [
                {
                    "op": "add",
                    "path": path,
                    "value": value
                } for path, value in fields.items()
            ],
            project=inputs.get("project_name"),
            type=inputs.get("type")
        )
<<<<<<< HEAD
        return CreateResult(id_="1", outs={"work item created": True})
=======
        return CreateResult(id_="1", outs={"work item id": work_item.id})

>>>>>>> Dev
    def create_wiki(
            self,
            inputs: dict
        ) -> CreateResult:
        wiki_params = WikiCreateParametersV2(
            name=inputs.get("wiki_name"), 
            project_id=inputs.get("project_id"), 
            type='projectWiki'
        )

        wiki_client = self.connection.clients.get_wiki_client()
        
        new_wiki = wiki_client.create_wiki(
            wiki_create_params=wiki_params, 
            project=inputs.get("project_id")
        )

        return CreateResult(id_="1", outs={"wiki id": new_wiki.id})
    
    def create_wiki_page(
            self,
            inputs: dict
        ) -> CreateResult:
        wiki_client = self.connection.clients.get_wiki_client()

        parameters = WikiPageCreateOrUpdateParameters(content=inputs.get("page_content"))

        wiki_client.create_or_update_page(
            parameters=parameters,
            project=inputs.get("project_id"),
            wiki_identifier=inputs.get("wiki_name"),  # This could be the wiki name or ID
            path=inputs.get("page_name"),
            comment='Adding a new wiki page',  # Optional comment for the commit
            version=None
        )

        return CreateResult(id_="1", outs={"wiki page created": True})
   

index = 0
class RestWrapper(Resource):
    def __init__(
            self,
            action_type: str,
            inputs: dict,
            opts=None,
        ) -> None:
        global index
        index += 1
        super().__init__(
            name=f"rest_wrapper_{index}",
            provider=RestAPI(),
            props={"action_type": action_type, **inputs},
            opts=opts
        )
    