from pulumi.dynamic import Resource, ResourceProvider, CreateResult
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from azure.devops.v7_1.work_item_tracking.models import CommentCreate
import configparser, random

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
        return CreateResult(id_="1", outs={"work item id": work_item.id})
    
    
    # def add_comment_to_work_item(self, project, work_item_id, comment_text, comment_format='Markdown'):
    #     """
    #     Adds a comment to a specified work item.

    #     :param str project: Project ID or project name.
    #     :param int work_item_id: ID of the work item to add the comment to.
    #     :param str comment_text: The text of the comment to add.
    #     :param str comment_format: The format of the comment (Markdown or Html). Default is Markdown.
    #     """
    #     # Get the WorkItemTrackingClient from the connection
    #     work_item_client = self.connection.clients.get_work_item_tracking_client()

    #     # Create the CommentCreate object with the provided comment text
    #     comment_request = CommentCreate(text=comment_text)

    #     # Call the add_work_item_comment method with the constructed request
    #     comment = work_item_client.add_work_item_comment(
    #         request=comment_request,
    #         project=project,
    #         work_item_id=work_item_id,
    #         format=comment_format
    #     )

    #     # Return the created comment object or its ID based on your needs
    #     return comment

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
    