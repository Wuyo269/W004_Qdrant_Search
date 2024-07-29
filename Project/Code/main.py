# ------------------------------------------
# Build in modules
# ------------------------------------------
None

# ------------------------------------------
# 3rd party modules (installation needed)
# ------------------------------------------
import requests

# ------------------------------------------
# custom modules
# ------------------------------------------
from Libraries.qdrant_custom.qdrant_custom import QdrantCustomClient

# Url to server containing data.
DATA_WEB_URL = 'https://unknow.news/archiwum_aidevs.json'


def retrieve_json_data_from_url(json_url: str) -> list[dict[str, any]]:
    """
    Retrieve data from specified url

    Parameters
    ----------
    json_url : str
        Url to server containing data.

    Returns
    -------
    list[dict[str, any]]
        List of data in dictionary format.
    """

    try:
        # Send get request to specified Url
        response = requests.get(url=json_url)
        # Check if request was successful.
        response.raise_for_status()
        # Parse JSON response.
        return response.json()
    except Exception as e:
        raise Exception(f"Failed to retrieve JSON data from URL - {e}")


class UserInterface():

    def __init__(self) -> None:
        self.answer_limit = 1
        self.qdrant_collection_name = "s004_qdrant_search"

    def help(self) -> None:
        """
        Print all commands available in Application
        Returns None
        -------
        """
        help_text = """Commands:
0 - Exit
1 - Check basic information
2 - Change limit answer
3 - Change collection name
4 - Upload data to qdrant vector database
5 - Search qdrant vector database
"""
        print(help_text)

    def execute(self) -> None:
        """
        Run application
        Returns None
        -------
        """
        print("Recipe book program")
        # Print available commands
        self.help()
        while True:
            command = input("Enter command:")
            if command == "0":
                break
            elif command == "1":
                self.check_basic_information()
            elif command == "2":
                self.change_answer_limit()
            elif command == "3":
                self.change_collection_name()
            elif command == "4":
                self.upload_data_to_qdrant()
            elif command == "5":
                self.get_answer_from_qdrant()
            else:
                self.help()

    def check_basic_information(self) -> None:
        """
        Pint out basic information:
        -collection name
        -limit answer

        Returns
        -------
        None
        """
        print(f"Collection name: {self.qdrant_collection_name}")
        print(f"Limit answer: {self.answer_limit}")

    def change_collection_name(self) -> None:
        """
        Change qdrant collection name that is used for application.

        Returns
        -------
        None
        """
        # Get user input
        new_collection_name = input("Provide collection name:")
        # Change value
        self.qdrant_collection_name = new_collection_name

    def change_answer_limit(self) -> None:
        """
        Change answer limit. This variable defines how may answer will be searched in qdrant vector database.

        Returns
        -------
        None
        """
        # Get user input
        new_answer_limit = input("Provide answer limit:")

        try:
            # Try to convert user input into integer
            new_answer_limit = int(new_answer_limit)
            self.answer_limit = new_answer_limit
        except Exception as e:
            print(f"Error: Answer limit has to be integer.")

    def upload_data_to_qdrant(self) -> None:
        """
        Upload data from url to qdrant.

        Returns
        -------
        None
        """
        try:
            # Get data from url
            data = retrieve_json_data_from_url(DATA_WEB_URL)

            # Create qdrant client
            qdrant_custom_client = QdrantCustomClient()

            # Make sure collection exists
            collection_exists = qdrant_custom_client.recreate_qdrant_collection(self.qdrant_collection_name)

            if not collection_exists:
                raise Exception(f"Collection '{self.qdrant_collection_name}' does not exist. Cannot continue script.")

            # Count points in qdrant collection
            qdrant_points = qdrant_custom_client.count_points(self.qdrant_collection_name)

            # If qdrant collection is not empty do not continue.
            if qdrant_points > 0:
                raise Exception(
                    f"Collection '{self.qdrant_collection_name}' is not empty. Clear collection before continuing the script.")

            # Upsert data
            qdrant_custom_client.upsert_qdrant_points(self.qdrant_collection_name, data)
            # Count points in qdrant collection
            qdrant_points = qdrant_custom_client.count_points(self.qdrant_collection_name)

            # If qdrant collection is not equal to data, raise exception
            if qdrant_points != len(data):
                raise Exception(f"Not all data was uploaded into collection {qdrant_points}/{len(data)}")
            print("Data upsert to qdrant vector database successfully.")
        except Exception as e:
            print(f"Error: {e}")

    def get_answer_from_qdrant(self) -> None:
        """
        Get information from qdrant vector database.
        The number of response can be changed by adjusting CONSTANT varialble 'LIMIT_ANSWER'

        Parameters
        ----------

        Returns
        -------
        None
            Data will be print out.
        """
        try:
            # Get question from user
            question = input("Write what do you want to know:")
            # Create qdrant client
            qdrant_custom_client = QdrantCustomClient()

            # Search qdrant for answer
            qdrant_answers = qdrant_custom_client.search_for_point(self.qdrant_collection_name, question,
                                                                   self.answer_limit)

            for index, answer in enumerate(qdrant_answers):
                print(f"Answer {index + 1}:")
                for key in answer.payload.keys():
                    print(f"{key}: {answer.payload[key]}")
                print("")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    # Create Instance of App
    app = UserInterface()
    # Run App
    app.execute()
