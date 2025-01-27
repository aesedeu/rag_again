import pandas as pd
import numpy as np
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from langchain_community.document_loaders import DataFrameLoader, TextLoader, PDFMinerLoader
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
import string
import os
import datetime as dt
import logging
from tqdm import tqdm
from pathlib import Path
from dotenv import load_dotenv
import yaml

config = yaml.safe_load(open('./config.yaml'))

load_dotenv()
PROJECT_DIRECTORY = os.getenv('PROJECT_DIRECTORY')
SOURCE_DOCUMENTS_FOLDER = os.getenv('SOURCE_DOCUMENTS_FOLDER')

log_name = f"{dt.datetime.now().strftime('%Y_%m_%d')}.log"
if log_name not in os.listdir("logs/"):
    Path(f"logs/{log_name}").touch()

logging.basicConfig(
    # filename='lll.log',
    # filemode='a',
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(f"logs/{dt.datetime.now().strftime('%Y_%m_%d')}.log"),
        logging.StreamHandler()
    ],
    level=logging.INFO
)

# EMBEDDINGS_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
# EMBEDDINGS_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
EMBEDDINGS_MODEL_NAME = "intfloat/multilingual-e5-small"
emb_func = SentenceTransformerEmbeddings(model_name=EMBEDDINGS_MODEL_NAME) # Модель для создания эмбеддингов


def get_texts(
        file_name:str,
        collection_name:str,
        chunk_size=300,
        chunk_overlap=100
    ):

    """
    This function is used to prepare the data for the vector store.
    It is used to load the dataset and split the documents into smaller chunks.
    
    file_name: str - full file's name
    chunk_size: int, default=300 - the size of the chunks to split the documents into
    chunk_overlap: int, default=100 - the overlap between the chunks
    """
    dataset_path = file_name
    logging.info(f'Выбраны данные из файла: {dataset_path}')

    if dataset_path.endswith('.txt'):
        loader = TextLoader(dataset_path)
    elif dataset_path.endswith('.pdf'):
        loader = PDFMinerLoader(dataset_path)
    
    documents = loader.load()  

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len
    )

    logging.info(f"Chunk size: {chunk_size}")
    logging.info(f"Chunk overlap: {chunk_overlap}")

    # Альтернативный вариант создания чанков через токенайзер LLM
    # text_splitter = RecursiveCharacterTextSplitter.from_huggingface_tokenizer(
    #     AutoTokenizer.from_pretrained("Open-Orca/Mistral-7B-OpenOrca"),
    #     chunk_size=chunk_size,
    #     chunk_overlap=chunk_overlap,
    #     separators=["\n\n", "\n", " ", ""]
    # )

    texts = text_splitter.split_documents(documents)


    def upload_to_vectorstore(texts, collection_name):

        """
        This function is used to upload the data to the vector store.
        It is used to upload the data to the vector store and create a collection.

        texts: list - the list of texts to upload to the vector store
        collection_name: str, default=None - the name of the collection to create in the vector store    
        """

        flag = True
        try:
            embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBEDDINGS_MODEL_NAME)
            logging.info("Загрузка модели для эмбеддингов: SUCCESS")
        except Exception as e:
            logging.info("Ошибка при загрузке модели эмбеддингов:", e)
            flag = False
            
        if flag:
            try:
                chroma_client = chromadb.HttpClient(
                    settings=Settings(
                        allow_reset=config['chromadb']['server_config']['allow_reset'],
                        chroma_api_impl=config['chromadb']['server_config']['chroma_api_impl'],
                        chroma_server_host=config['chromadb']['server_config']['chroma_server_host'],
                        chroma_server_http_port=config['chromadb']['server_config']['chroma_server_http_port'],
                        anonymized_telemetry=config['chromadb']['server_config']['anonymized_telemetry']
                        )
                    )
                logging.info("Подключение к CHROMADB: SUCCESS")
            except Exception as e:
                logging.info("Ошибка при подключении к CHROMADB:", e)
                flag = False
        
        if flag:
            for i in chroma_client.list_collections():
                if i.name == collection_name:
                    chroma_client.delete_collection(collection_name)
                    logging.info(f'Была обнаружена и удалена существующая коллекция с именем "{collection_name}"')
            try:
                collection = chroma_client.get_or_create_collection(name=collection_name,
                                                metadata={"hnsw:space": "cosine"},
                                                embedding_function=embedding_function
                                                )
                logging.info(f"Создание коллекции {collection_name}: SUCCESS")
            except Exception as e:
                logging.info("Ошибка при создании коллекции:", e)
                flag = False
        
        if flag:
            try:
                counter = 0
                for doc in texts:
                    counter += 1
                    # if counter % 100 == 0:
                    #     logging.info(f"uploaded {counter} of {len(texts)}")
                    collection.add(
                        documents=doc.page_content,
                        metadatas=doc.metadata,
                        ids=['id'+str(counter)]
                        # ids=doc.metadata['id']
                    )
                logging.info("Загрузка данных в CHROMADB: SUCCESS")
            except Exception as e:
                logging.info("Ошибка при загрузке данных в CHROMADB:", e)
    
    upload_to_vectorstore(
        texts=texts,
        collection_name=collection_name
    )
    # return texts


def get_chroma_client():
    """
    This function is used to get the chroma client.
    It is used to get the chroma client to connect to the vector store.
    
    Returns: chroma_client - the chroma client to connect to the vector store"""
    try:
        chroma_client = chromadb.HttpClient(
            settings=Settings(
                allow_reset=config['chromadb']['server_config']['allow_reset'],
                chroma_api_impl=config['chromadb']['server_config']['chroma_api_impl'],
                chroma_server_host=config['chromadb']['server_config']['chroma_server_host'],
                chroma_server_http_port=config['chromadb']['server_config']['chroma_server_http_port'],
                anonymized_telemetry=config['chromadb']['server_config']['anonymized_telemetry']
                )
            )
        logging.info("Подключение к CHROMADB: SUCCESS")
        logging.info("Доступны следующие коллекции:")
        for i in chroma_client.list_collections():
            logging.info(f"- {i.name}")
        return chroma_client
    except Exception as e:
        logging.info("Ошибка при подключении к CHROMADB:", e)
        return None

def vectorstore_query(collection, source_file_type, question, n_results):
    """
    This function is used to query the vector store.
    It is used to query the vector store to get the response to a question.
    
    collection: collection - the collection to query in the vector store
    source_file_type: str - type of file which was used for collection creating
    question: str - the question to query in the vector store
    n_results: int - the number of results to return
    """

    response = collection.query(
        query_embeddings=emb_func.embed_query(question), # Векторный поиск происходит через эмбеддинг, который создается той же моделью, что и в chromadb
        # query_texts=question,
        n_results=n_results
    )
        
    if source_file_type.lower() in ['txt']:
        vector_db_response = " ".join(response["documents"][0])
    
    elif source_file_type.lower() in ['pdf']:
        vector_db_response = ''
        for doc in response['documents'][0]:
            for i in doc:
                if i in string.punctuation or i in "«»": 
                    doc = doc.replace(i, '').replace("\n","")
            vector_db_response += doc.capitalize() + ". "

    return vector_db_response
