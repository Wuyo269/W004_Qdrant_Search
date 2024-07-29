# ------------------------------------------
# Build in modules
# ------------------------------------------
import os
import uuid
from typing import Optional, Tuple, List, Dict, Any

# ------------------------------------------
# 3rd party modules (installation needed)
# ------------------------------------------

from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.grpc import ScoredPoint
from qdrant_client.http.exceptions import ResponseHandlingException
from qdrant_client.models import VectorParams, Distance, Batch

# ------------------------------------------
# custom modules
# ------------------------------------------
None


class QdrantCustomClient():

    def __init__(self, collection_name):
        self.__api_key__ = self.get_api_from_env_variable()
        self.__url___ = self.get_url_from_env_variable()
        self.collection_name = collection_name
        self.vector_size = 1536
        self.qdrant_client = self.initialize_qdrant_client()
        self.open_ai_client = OpenAI()
        self.open_ai_embedding_model = "text-embedding-ada-002"

    def get_env_variable(self, environment_variable_name: str):
        """
        Get environment variable value. Raise error if variable does not exists in system.
        Parameters
        ----------
        environment_variable_name :str
            Environment variable name.

        Returns
        -------
        str
            Environment variable value
        """

        environment_variable_value = os.getenv(environment_variable_name)
        if environment_variable_value == None:
            raise Exception(
                f"Environment variable '{environment_variable_name}' not available. Create new environment variable or restart computer if already created.")
        else:
            return environment_variable_value

    def get_url_from_env_variable(self):
        """
        Get environment variable value for 'QDRANT_URL'. Raise error if variable does not exists in system.

        Returns
        -------
            Environment variable value for 'QDRANT_URL'
        """

        qdrant_url = self.get_env_variable("QDRANT_URL")
        # qdrant_url = "https://fd7d3daa-dcad-40c7-9b9b-bdff8070044c.europe-west3-0.gcp.cloud.qdrant.io:6333"
        return qdrant_url

    def get_api_from_env_variable(self):
        """
        Get environment variable value for 'QDRANT_API_KEY'. Raise error if variable does not exists in system.

        Returns
        -------
            Environment variable value for 'QDRANT_API_KEY'
        """

        qdrant_apikey = self.get_env_variable("QDRANT_API_KEY")
        return qdrant_apikey

    def initialize_qdrant_client(self) -> QdrantClient:
        """
        Initialize Qdrant client with provided URL and API Key

        Returns
        -------
        QdrantClient
            The initialized Qdrant client.
        """

        try:
            self.qdrant_client = QdrantClient(
                url=self.__url___,
                api_key=self.__api_key__,
            )
            return self.qdrant_client
        except ResponseHandlingException as e:
            raise Exception(f"Failed to initialize Qdrant client: {e}")

    def collection_exists(self, collection_name: str) -> bool:
        """
        Check if collection exists in the Qdrant client.

        Parameters
        ----------
        collection_name : str
            The name of the collection to check.

        Returns
        -------
        bool
            True if collection exists, False otherwise.
        """

        return self.qdrant_client.collection_exists(collection_name)

    def create_collection(self, collection_name: str) -> bool:
        """
        Create collection for Qdrant client.

        Parameters
        ----------
        collection_name.
            The name of collection to create.

        Returns
        -------
        bool
            True if collection was created, False otherwise.
        """

        try:
            # Create config
            vectors_config = VectorParams(size=self.vector_size, distance=Distance.COSINE)
            # Create collection
            self.qdrant_client.create_collection(collection_name=collection_name, vectors_config=vectors_config)
            # Check if the collection was created successfully.
            return self.collection_exists(collection_name)
        except Exception as e:
            raise Exception(f"Error during creating collection '{collection_name}' - {e}")

    def recreate_qdrant_collection(self, collection_name: str) -> bool:
        """
        Make sure that collection exists in the Qdrant client. If it does not exist, create it.

        Parameters
        ----------
        collection_name : str
            The name of the collection to recreate.

        Returns
        -------
        bool
            True if collection already exist or was created, False if collection was not created.
        """

        # Check if collection exists
        collection_exist = self.collection_exists(collection_name)
        # Create collection if it does not exist.
        if not collection_exist:
            collection_exist = self.create_collection(collection_name)

        return collection_exist

    def count_points(self, collection_name: str) -> int:
        """
        Get number of items (points) from specified collection.

        Parameters
        ----------
        collection_name : str
            The name of collection from which to retrieve points.

        Returns
        -------
        int
            Number of items (points) in specified collection.
        """

        try:
            # Get qdrant collection
            response = self.qdrant_client.get_collection(collection_name=collection_name)
            # Count points (items)
            return response.points_count
        except BaseException as e:
            raise Exception(f"Failed to retrieve Qdrant collection's '{collection_name}' points -  {e}")

    def create_embedding(self, input_text: str) -> list[float]:
        """
        Convert string into embedding. Return list of numbers from -1 to 1.

        Parameters
        ----------
        input_text : str
            Text to be converted into list of numbers.

        Returns
        -------
        list[float]
            List of integers from -1 to 1 representing the embedded word.
        """

        try:
            # Get response from embedding model
            response = self.open_ai_client.embeddings.create(model=self.open_ai_embedding_model, input=input_text)
            # Convert to dict
            embedding = response.model_dump()
            # Get embedding result
            result = embedding["data"][0]["embedding"]
            return result
        except Exception as e:
            raise Exception(f"Failed to request embeddings from the embeddings API: {e}")

    def upsert_qdrant_points(self,
                             collection_name: str,
                             json_data: List[Dict[str, str]],
                             embedding_key_name: str = "info"
                             ) -> None:
        """
        Upload data to specified collection in Qdrant.

        Parameters
        ----------
        collection_name : str
            The name of collection to which the data will be upserted..
        json_data : list[dict[str,str]]
            List of data in dictionary format.
        embedding_key_name : str
            Key of dictionary that contains text to be used in embedding process.

        Returns
        -------
        None
        """

        ids = []
        payloads = []
        vectors = []
        counter = 0

        # Prepare points
        for json_item in json_data:
            # Generate unique Id for each point
            ids.append(str(uuid.uuid4()))
            # Add json item to playloads
            payloads.append(json_item)
            # Create embedding
            vectors.append(
                self.create_embedding(input_text=json_item[embedding_key_name])
            )

            # Display progress of method
            counter += 1
            if counter % 100 == 0:
                print(f"Prepare json: {counter}")

        try:
            self.qdrant_client.upsert(
                collection_name=collection_name,
                points=Batch(
                    ids=ids,
                    payloads=payloads,
                    vectors=vectors,
                ),
            )

        except Exception as e:
            raise Exception(f"Failed to upsert points to Qdrant for collection '{collection_name}': {e}")

    # CHeckedc
    # CHeckedc
    # CHeckedc

    def search_for_point(self,
                         collection_name: str,
                         question: str,
                         answers_limit: int = 1
                         ) -> list[ScoredPoint]:
        """
        Find information in Vector database. You may change the number of returned answers by adjusting the 'answers_limit' argument.

        Parameters
        ----------
        collection_name :str
            The name of collection in which the search will be performed.
        question : str
            The question used to find the closest information in vector database.
        answers_limit : int
            Number of answers return by vector database. Default is 1.

        Returns
        -------
        list[ScoredPoint]
            Answers found in the collection. Number of answers found is limited to value of 'answers_limit'.
        """

        # Convert question into embedding.
        question_vector = self.create_embedding(input_text=question)

        try:
            answers = self.qdrant_client.search(
                collection_name=collection_name,
                query_vector=question_vector,
                limit=answers_limit,
            )

            return answers
        except Exception as e:
            raise Exception(f"Failed to search for point in Qdrant for collection '{collection_name}'- {e}.")


# Test imports
import json

# test __init__
if False:
    collection_name = "pandora"
    qdrant_custom_client = QdrantCustomClient(collection_name)
    print("Check")

# test collection_exists
if False:
    collection_name = "pandora"
    qdrant_custom_client = QdrantCustomClient(collection_name)
    a = qdrant_custom_client.collection_exists(collection_name)
    b = qdrant_custom_client.collection_exists("Matki")

    print("Check")

# test create_collection
if False:
    collection_name = "Euro 202"
    qdrant_custom_client = QdrantCustomClient(collection_name)
    created = qdrant_custom_client.create_collection(collection_name)
    print("Check")

# test recreate collection
if True:
    collection_name = "pandora2013"
    qdrant_custom_client = QdrantCustomClient(collection_name)
    test1 = qdrant_custom_client.recreate_qdrant_collection(collection_name)
    print("Check")
    collection_name = "testdel"
    qdrant_custom_client = QdrantCustomClient(collection_name)
    test2 = qdrant_custom_client.recreate_qdrant_collection(collection_name)
    print("Check")

# test count_points
if False:
    collection_name = "test_connection"
    qdrant_custom_client = QdrantCustomClient(collection_name)
    points = qdrant_custom_client.count_points(collection_name)
    print("Check")

    collection_name = "test_connection_does not work"
    qdrant_custom_client = QdrantCustomClient(collection_name)
    points = qdrant_custom_client.count_points(collection_name)
    print("Check")

# test create_embedding
if False:
    collection_name = "test_connection"
    input_text = "Bochenek chleba"

    qdrant_custom_client = QdrantCustomClient(collection_name)
    input_embeding = qdrant_custom_client.create_embedding(input_text)

    print("Check")

# test upsert_qdrant_points
if False:
    data = "test_data.txt"

    with open(data, "r", encoding="utf-8") as file:
        json_data = json.load(file)

    collection_name = "test_connection"

    qdrant_custom_client = QdrantCustomClient(collection_name)
    qdrant_custom_client.upsert_qdrant_points(collection_name, json_data, "info")

    print("Check")

# test search_for_point
if False:
    collection_name = "test_connection"
    input_text = "Chciabym wiedzieć jak integrować się z API"

    qdrant_custom_client = QdrantCustomClient(collection_name)
    answer = qdrant_custom_client.search_for_point(collection_name, input_text)

    print("Check")
