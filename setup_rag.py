from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings

# Initialize the embedding model for creating document embeddings
embeddings = OllamaEmbeddings(model='nomic-embed-text')

# Load and preprocess the document (PDF)
loader = PyPDFLoader(file_path="Food Delivery Complaint Handling Rule Book.pdf")
# Split the document into smaller chunks of text for easier processing
text_splitter = CharacterTextSplitter.from_tiktoken_encoder(chunk_size=150, chunk_overlap=30)
doc_splits = loader.load_and_split(text_splitter)  # This returns a list of smaller text chunks

# Create a Chroma vector store to hold the document embeddings
vectorstore = Chroma.from_documents(
    documents=doc_splits,  # The list of document chunks
    collection_name="rag-chroma",  # The name of the collection in the vector store
    embedding=embeddings,  # The embedding model to transform documents into vectors
)

# Create a retriever to perform searches on the vector store
retriever = vectorstore.as_retriever(search_kwargs={"k": 1})  # Limit the search to the top 1 result

def get_rag(query: str):
    """Returns information based on the query using RAG (Retrieval-Augmented Generation).
    Takes a string query as input and retrieves the most relevant document chunk.
    """
    result = retriever.invoke(query)[0]  # Invoke the retriever with the query and get the top result
    return result  # Return the result from the retriever