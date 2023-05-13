from dotenv import load_dotenv

from langchain.document_loaders import TextLoader, DirectoryLoader

from langchain.text_splitter import CharacterTextSplitter

from langchain.embeddings import OpenAIEmbeddings

from langchain.vectorstores import Chroma

from chromadb.config import Settings

from langchain.chains import RetrievalQAWithSourcesChain

from langchain.chat_models import ChatOpenAI

import os

load_dotenv()

ABS_PATH: str = os.path.dirname(os.path.abspath(__file__))
DB_DIR: str = os.path.join(ABS_PATH, "db")

# doc_loader: TextLoader = TextLoader('index.js.txt', encoding="utf8")

# document: str = doc_loader.load()

# text_splitter: CharacterTextSplitter = CharacterTextSplitter(
#     chunk_size=512, chunk_overlap=0)

# split_docs: list[str] = text_splitter.split_documents(document)

loader = DirectoryLoader("output/*", glob="*.txt")
txt_docs = loader.load_and_split()

# txt_docsearch = Chroma.from_documents(txt_docs, embeddings)

openai_embeddings: OpenAIEmbeddings = OpenAIEmbeddings()


client_settings: Settings = Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory=DB_DIR,
    anonymized_telemetry=False
)
if not os.path.exists(DB_DIR):
    vector_store: Chroma = Chroma.from_documents(txt_docs, openai_embeddings,  persist_directory=DB_DIR,
                                                 client_settings=client_settings,
                                                 collection_name="transcripts_store")

    vector_store.persist()
else:
    vector_store: Chroma = Chroma(collection_name="transcripts_store", persist_directory=DB_DIR,
                                  embedding_function=openai_embeddings, client_settings=client_settings)

qa_with_source: RetrievalQAWithSourcesChain = RetrievalQAWithSourcesChain.from_chain_type(
    llm=ChatOpenAI(temperature=0, model_name='gpt-3.5-turbo'),
    chain_type="stuff",
    # retriever=vector_store.as_retriever()
    retriever=vector_store.as_retriever(search_kwargs={"k": 1})
)

def query_document(question: str) -> dict[str, str]:
    return qa_with_source({"question": question})

user_query: str = input("\033[33m")
query_document(user_query)


while (True):
    print("What is your query? ", end="")
    user_query: str = input("\033[33m")
    print("\033[0m")
    if (user_query == "quit"):
        break
    response: dict[str, str] = query_document(user_query)
    print(f'Answer: \033[32m{response["answer"]}\033[0m')
    print(f'\033[34mSources: {response["sources"]}\033[0m')
