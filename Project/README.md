## Description
Script is a text application to communicate with Qdrant vector database.<br>
Functionalities:
1. Check basic information
2. Change limit answer
3. Change collection name
4. Upload data to qdrant vector database
5. Search qdrant vector database

## Prerequisites
Qdrant:
1. Create account on https://qdrant.tech/
2. Create cluster. The name of the cluster in not important.
3. Create API for cluster. Once you create API you will receive API Key and URl.
4. Save API Key in System environment variable as "QDRANT_API_KEY"
5. Save URL in System environment variable as "QDRANT_URL"
6. Restart computer, system environment variable are not available otherwise.

OpenAI:
1. Create account on https://platform.openai.com/
2. Create API Key.
3. Save API Key in System environment variable as "OPENAI_API_KEY"
4. Restart computer, system environment variable are not available otherwise.


## Tech Info
Python Version: Python 3.12.3

##	Input file	
There is no input file.
Data for Vector database needs to be downloaded and upsert to qdrant database using application. <br>
Command: 4. Upload data to qdrant vector database


## 	Requirements
All requirements are listed in 'requirements.txt' file.

## Run Script
To script run "main.py" file.
