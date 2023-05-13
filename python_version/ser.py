from http.server import BaseHTTPRequestHandler, HTTPServer
import git
import os
from dotenv import load_dotenv

from langchain.document_loaders import TextLoader, DirectoryLoader

from langchain.text_splitter import CharacterTextSplitter

from langchain.embeddings import OpenAIEmbeddings

from langchain.vectorstores import Chroma

from chromadb.config import Settings

from langchain.chains import RetrievalQAWithSourcesChain

from langchain.chat_models import ChatOpenAI
import threading

load_dotenv()

ABS_PATH: str = os.path.dirname(os.path.abspath(__file__))
DB_DIR: str = os.path.join(ABS_PATH, "db")

def getAnswer(git_folder_name): 
    loader = DirectoryLoader(f"output/{git_folder_name}/*", glob="*.txt")
    txt_docs = loader.load_and_split()

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
        retriever=vector_store.as_retriever(search_kwargs={"k": 1})
    )

    def query_document(question: str) -> dict[str, str]:
        return qa_with_source({"question": question})

    response: dict[str, str] = query_document('For what purposes this project?')
    print(f'Answer: \033[32m{response["answer"]}\033[0m')
    print(f'\033[34mSources: {response["sources"]}\033[0m')
    return response


def txtFormatter(git_folder_name):
    source_dir = f'./test/{git_folder_name}'

    output_dir = f'./output/{git_folder_name}'

    file_types = ('.md', '.js', '.ts', '.json', '.css', '.sql', '.html')

    readme_file = None

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if file.endswith(file_types) and file != 'README.md':
                input_file_path = os.path.join(root, file)
                relative_path = os.path.relpath(input_file_path, source_dir)
                new_root = root.replace(source_dir, output_dir)
                output_file_path = os.path.join(
                    new_root, f'{os.path.splitext(file)[0]}.{os.path.splitext(file)[1][1:]}.txt')

                if not os.path.exists(new_root):
                    os.makedirs(new_root)

                with open(input_file_path, 'r', encoding='ISO-8859-1') as infile, open(output_file_path, 'w', encoding='ISO-8859-1') as outfile:
                    outfile.write(
                        f'This is a txt representation of the VirtueMaster file located at {relative_path}\n\n')
                    outfile.write(infile.read())

            elif file == 'README.md':
                readme_input_file_path = os.path.join(root, file)
                readme_relative_path = os.path.relpath(
                    readme_input_file_path, source_dir)

    if readme_file:
        readme_new_root = readme_input_file_path.replace(
            source_dir, output_dir)
        readme_output_file_path = os.path.join(os.path.dirname(
            readme_new_root), f'{os.path.splitext("README.md")[0]}.{os.path.splitext("README.md")[1][1:]}.txt')
        with open(readme_input_file_path, 'r', encoding='ISO-8859-1') as infile, open(readme_output_file_path, 'w', encoding='ISO-8859-1') as outfile:
            outfile.write(
                f'This is a txt representation of the VirtueMaster file located at {readme_relative_path}\n\n')
            outfile.write(infile.read())


folder_name = "test"

current_dir = os.getcwd()

new_folder_path = os.path.join(current_dir, folder_name)

if not os.path.exists(new_folder_path):
    os.mkdir(new_folder_path)

hostName = "localhost"
serverPort = 8080

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        params = {}
        response_text = "{ \"downloaded\": true }"
        if '?' in self.path:
            query = self.path.split('?', 1)[1]
            params = dict(qc.split('=') for qc in query.split('&'))
        if 'git' in params:
            git_folder_name = params['git'].split('/')[-1]
            if not os.path.exists(os.path.join(current_dir, folder_name, git_folder_name)):
                git.Git(os.path.join(os.getcwd(), folder_name)).clone(
                    "https://github.com/" + params['git'])
            txtFormatter(git_folder_name)
            response_text = "{ \"Success\":" + getAnswer(git_folder_name) + " }"
        else:
            response_text = "{ \"something_wrong\": true }"
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(response_text, "utf-8"))


if __name__ == "__main__":
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInter8rupt:
        pass

    webServer.server_close()
    print("Server stopped.")
