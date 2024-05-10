from pulumi.dynamic import Resource, ResourceProvider, CreateResult
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from azure.devops.v7_1.work_item_tracking.models import CommentCreate
from azure.devops.v7_1.wiki.models import WikiCreateParametersV2
from azure.devops.v7_1.wiki.models import WikiPageCreateOrUpdateParameters
import time
from source.config import USERNAME, PAT, ORGANIZATION_NAME

has_been_called = False

class RestAPI(ResourceProvider):
    """
    Provides a resource provider that interacts with Azure DevOps services, allowing operations such as running pipelines,
    creating work items, and managing wikis through specified actions.
    """   
    def create(self, inputs: dict) -> CreateResult:
        """
        Creates a resource in Azure DevOps based on specified action type and inputs.

        Args:
            inputs (dict): Details necessary for resource creation

        Returns:
            CreateResult: An instance representing the outcome of the resource creation process.

        Raises:
            Exception: If the action type provided is not supported.

        Example:
            >>> api = RestAPI()
            >>> api.create({'action_type': 'run_pipeline', 'branch': 'main', 'project_name': 'SampleProject', 'pipeline_id': 123})
        """
        self.has_called_workitem = False
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
        elif action_type == "create_wiki_with_content":
            return self.create_wiki_with_content(inputs)
        else:
            raise Exception("Invalid action type")

    def run_pipeline(
            self,
            inputs: dict
        ) -> CreateResult:
        """
        Initiates a pipeline run based on provided input details.

        Args:
            inputs (dict): Contains the necessary details for the pipeline run.

        Returns:
            CreateResult: An object encapsulating the ID of the initiated pipeline run and any outputs.

        Example:
            >>> api = RestAPI()
            >>> api.run_pipeline({'branch': 'main', 'project_name': 'ExampleProject', 'pipeline_id': 101})
        """
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
        """
        Creates a work item in Azure DevOps with specified attributes and optionally adds comments.

        Args:
            inputs (dict): Details for the work item to be created

        Returns:
            CreateResult: An object encapsulating the ID of the created work item and any outputs.

        Example:
            >>> api = RestAPI()
            >>> api.create_work_item({
                    'title': 'Fix login issue',
                    'description': 'Error on authentication',
                    'assigned_to': 'dev@example.com',
                    'project_name': 'ProjectX',
                    'type': 'Bug',
                    'comments': ['Initial bug report', 'Urgent fix needed'],
                    'state': 'Active'
                })
        """
        global has_been_called

        work_item_client = self.connection.clients.get_work_item_tracking_client()

        if not has_been_called:
            time.sleep(60)
            has_been_called = True
        
        fields = {
            "/fields/System.Title": inputs.get("title"),
            "/fields/System.Description": inputs.get("description"),
        }

        if inputs.get("assigned_to") != None:
            fields["/fields/System.AssignedTo"]=(inputs.get("assigned_to"))

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

        if len(inputs.get("comments")) != 0:
            
            comments = [CommentCreate(text=comment) for comment in inputs.get("comments")]  

            for comment in comments:
                work_item_client.add_comment(
                    request=comment,
                    project=inputs.get("project_name"),
                    work_item_id=work_item.id
                )

        if inputs.get("state") != "New":
            inputs.update({"work_item_id": work_item.id})
            self.update_work_item_state(inputs, work_item_client)

        return CreateResult(id_="1", outs={"work item id": work_item.id})

    def update_work_item_state(
            self,
            inputs: dict,
            work_item_client
        ) -> CreateResult:
        """
        Updates the state of an existing work item in Azure DevOps based on the specified inputs.

        Args:
            inputs (dict): Details for the work item to be updated.
            work_item_client (WorkItemTrackingClient): The client used to interact with work item tracking service.

        Returns:
            CreateResult: An object encapsulating the ID of the updated work item and any outputs.

        Example:
            >>> api = RestAPI()
            >>> work_item_client = WorkItemTrackingClient()
            >>> api.update_work_item_state({
                    'state': 'Resolved',
                    'project_name': 'ProjectX',
                    'work_item_id': '456'
                }, work_item_client)
        """
        fields = {
            "/fields/System.State": inputs.get("state")
        }

        work_item = work_item_client.update_work_item(
            document = [
                {
                    "op": "add",
                    "path": path,
                    "value": value
                } for path, value in fields.items()
            ],
            project=inputs.get("project_name"),
            id=inputs.get("work_item_id")
        )

        return CreateResult(id_="1", outs={"work item id": work_item.id})

    def create_wiki_with_content(
            self,
            inputs: dict
            ) -> CreateResult:
        """
        Creates a wiki in Azure DevOps and adds a content page based on the specified inputs. This method handles the
        creation of both the wiki and its initial page.

        Args:
            inputs (dict): Details necessary for creating the wiki and its page, including:

        Returns:
            CreateResult: An object encapsulating the success status and identifiers related to the created wiki and page.

        Example:
            >>> api = RestAPI()
            >>> api.create_wiki_with_content({
                    'wiki_name': 'Project Wiki',
                    'project_id': 'project123',
                    'page_content': 'Welcome to the new project wiki page!',
                    'page_name': 'Home'
                })
        """
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

        CreateResult(id_="1", outs={"wiki id": new_wiki.id})

        parameters = WikiPageCreateOrUpdateParameters(content=inputs.get("page_content"))

        wiki_client.create_or_update_page(
            parameters=parameters,
            project=inputs.get("project_id"),
            wiki_identifier=inputs.get("wiki_name").replace(" ", "-"),
            path=inputs.get("page_name"),
            comment='Adding a new wiki page',
            version=None
        )

        return CreateResult(id_="1", outs={"wiki page created": True})

index = 0
class RestWrapper(Resource):
    """
    A resource management layer that delegates actions like create, update, and delete to an underlying RestAPI provider
    based on provided inputs. This class abstracts the complexity of directly interacting with the API, providing
    a simpler interface for managing resources.

    Args:
        action_type (str): The type of action this resource will manage.
        inputs (dict): Parameters necessary for the specified action, tailored to the needs of the RestAPI.
        opts (optional): Optional configuration options that might be necessary for resource management or action customization.
    
    Example:
        >>> rest_wrapper = RestWrapper(
                action_type="run_pipeline",
                inputs={
                    "branch": "main",
                    "project_name": "SampleProject",
                    "pipeline_id": 123
                }
            )
    """
    def __init__(
            self,
            action_type: str,
            inputs: dict,
            opts=None,
        ) -> None:
        """
        Initializes a new instance of RestWrapper.

        This constructor sets up the RestWrapper with a unique name by incrementing a global index, assigns the RestAPI
        provider to it, and passes the action and inputs down to the RestAPI.

        Args:
            action_type (str): The type of action this resource is meant to manage (e.g., 'create', 'update', 'delete').
            inputs (dict): A dictionary containing all the parameters necessary for executing the specified action.
            opts (optional): Additional options for the Pulumi resource, such as dependencies or parent resources.

        Notes:
            The global index is incremented on each instantiation to ensure unique resource names for each instance, which
            helps in avoiding name conflicts in the resource management system.
        """
    
        global index
        index += 1
        super().__init__(
            name=f"rest_wrapper_{index}",
            provider=RestAPI(),
            props={"action_type": action_type, **inputs},
            opts=opts
        )
    