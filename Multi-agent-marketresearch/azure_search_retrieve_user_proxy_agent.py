from typing import Callable, Dict, List, Optional
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
import logging
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import SearchIndex, SimpleField
from azure.search.documents import SearchClient
import os

logger = logging.getLogger(__name__)



class AzureSearchRetrieveUserProxyAgent(RetrieveUserProxyAgent):
    def __init__(
        self,
        name="RetrieveChatAgent",
        human_input_mode: Optional[str] = "ALWAYS",
        is_termination_msg: Optional[Callable[[Dict], bool]] = None,
        retrieve_config: Optional[Dict] = None,
        **kwargs,
    ):
        """
        Initialization for AzureSearchRetrieveUserProxyAgent with Azure Cognitive Search specifics.
        """
        super().__init__(name, human_input_mode, is_termination_msg, retrieve_config, **kwargs)

        self.index_name: str = self._retrieve_config.get("index_name", "")  # Add type hint and handle None case
        if not self.index_name:
            raise ValueError("index_name cannot be None.")

        self.endpoint: str = self._retrieve_config.get("endpoint") or ""
        if not self.endpoint:
            raise ValueError("endpoint cannot be None.")

        self.api_key: Optional[str] = self._retrieve_config.get("api_key") or ""
        if self.api_key == "":
            raise ValueError("api_key cannot be None.")

        self._client = SearchClient(endpoint=self.endpoint,
            index_name=self.index_name,
            credential=AzureKeyCredential(self.api_key or ""))
        

    def retrieve_docs(self, problem: str, n_results: int = 20, search_string: str = ""):
        """
        Retrieves documents from Azure Cognitive Search.
        """
        results = self.ai_search_query(problem=problem, n_results=n_results, search_string=search_string)
        self._results = results

    def ai_search_query(self, problem: str, n_results: int = 20, search_string: str = "") -> Dict:
        """
        Perform a search query against Azure Cognitive Search.

        Args:
            problem (str): The problem to be solved.
            n_results (int): Number of results to return.
            search_string (str): A specific search string to filter results.

        Returns:
            List[Dict]: A list of dictionaries, each representing a document matching the search criteria.
        """
        # Construct search parameters
        search_params = {
            "search_text": problem,
            "include_total_count": True,
            "top": n_results,
        }
        if search_string:
            # You might want to adjust the filter syntax based on your Azure Cognitive Search index setup
            search_params["filter"] = f"document/any(d: d eq '{search_string}')"

        results = self._client.search(**search_params)

        ids, documents, metadatas, score, embeddings, uris = [], [], [], [], [], []
        for result in results:
            ids.append(result["id"])
            documents.append(result.get("content"))  # Assuming 'content' holds the document text
            metadatas.append({key: value for key, value in result.items() if key not in ["id", "content", "@search.score"]})
            score.append(result["@search.score"])
            embeddings.append(result.get("embedding"))
            uris.append(result.get("url"))


        return {
            'ids': [ids],  # Nested lists to match the specified structure
            'distances': [score],  # Distances if available
            'metadatas': [metadatas],  # Metadata excluding the id and content
            'embeddings': [embeddings],  # Embeddings if available
            'documents': [documents],  # Actual document content
            'uris': [uris],  # URIs if available
            'data': None,  # Additional data placeholder if needed
        }

    from typing import List


    def read_documents_from_dir(self, dir_path: str, custom_text_types: List[str], recursive: bool) -> List[dict]:
        documents = []
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                if any(file.endswith(ext) for ext in custom_text_types):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8') as file_content:
                        documents.append({"@search.action": "upload", "id": os.path.splitext(file)[0], "content": file_content.read()})
            if not recursive:
                break
        return documents

    def upload_documents_in_batches(self, search_client, documents: List[dict], batch_size: int = 1000):
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i+batch_size]
            search_client.upload_documents(documents=batch)

    def create_Azure_search_from_dir(
            self,
            custom_text_types: List[str] = ['txt'],
            recursive: bool = True,
        ):
        admin_client = SearchIndexClient(endpoint=self.endpoint, credential=AzureKeyCredential(self.api_key))
        fields=[
            SimpleField(name="id", type=edm.String, searchable=False, filterable=True, sortable=True, facetable=False, key=True),
            SimpleField(name="content", type=edm.String, searchable=True, filterable=False, sortable=False, facetable=False),
        ]
        index = SearchIndex(name=self.index_name, fields=fields)

        if not admin_client.get_index(self.index_name):
            admin_client.create_index(index)

        search_client = SearchClient(endpoint=self.endpoint, index_name=self.index_name, credential=AzureKeyCredential(self.api_key))

        documents = self.read_documents_from_dir(self._docs_path, custom_text_types, recursive)
        try:
            self.upload_documents_in_batches(search_client, documents)
        except Exception as e:
            print(f"An error occurred: {e}")


# Example usage
if __name__ == "__main__":
    azure_retrieve_config = {
        "endpoint": search_endpoint,
        "index_name": index_name,
        "api_key": search_api_key,
        "docs_path": None,
    }
    agent = AzureSearchRetrieveUserProxyAgent(retrieve_config=azure_retrieve_config)
    agent.retrieve_docs("what is sppi?")
    print(len(agent._results))
   
    # conver the results to pandas dataframe
    # import pandas as pd
    # df = pd.DataFrame(agent._results, columns=agent._results.keys())

    # print(df.head())

