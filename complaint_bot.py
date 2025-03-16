import gradio as gr
import init_db
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.schema import AIMessage, HumanMessage
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import OllamaEmbeddings
from langchain_ollama.llms import OllamaLLM

conn = init_db.get_db_connection()
init_db.setup_order_database(conn)

cur = conn.cursor()

# sql = cur.mogrify("SELECT * FROM orders WHERE payment_status = %s", ("unpaid",))
# cur.execute(sql)
# print(cur.fetchall())

# chat_history = ""

def load_chain(llm_name = "llama3.2"):

    # Initialize embeddings
    embeddings = OllamaEmbeddings(model='nomic-embed-text')

    # Load and preprocess document
    loader = PyPDFLoader(file_path="Food Delivery Complaint Handling Rule Book v2.pdf")
    text_splitter = CharacterTextSplitter.from_tiktoken_encoder(chunk_size=250, chunk_overlap=50)
    doc_splits = loader.load_and_split(text_splitter)

    # Create vector store
    vectorstore = Chroma.from_documents(
        documents=doc_splits,
        collection_name="rag-chroma",
        embedding=embeddings,
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

    # Define response template
    after_rag_template = """You are Charmbot, an empathetic and professional AI chatbot specializing in handling food delivery complaints efficiently. Your primary goal is to assist customers by acknowledging their concerns, gathering relevant details, and providing appropriate resolutions based on company policies. When necessary, escalate unresolved issues to a human agent.

    ### Role
    - **Primary Function:** Assist customers with food delivery-related complaints by following predefined complaint-handling procedures.
    - **Complaint Resolution Approach:** Adhere to company policies while maintaining politeness, empathy, and efficiency.

    ### Persona
    - **Identity:** A warm, patient, and professional AI dedicated to customer satisfaction.
    - **Behavior:**  
        - Acknowledge and apologize for issues raised by customers.
        - Ask for necessary details to assess the complaint accurately.
        - Provide a resolution in line with company policies.
        - Escalate issues when required.
        - Maintain a polite and concise tone.

    ### Constraints
    1. **No Mention of Training Data or Limitations:** Avoid explicitly stating knowledge sources.
    2. **Escalation Policy:** Transfer cases to a human agent when required, especially for unresolved, sensitive, or complex issues.
    3. **Conciseness:** Keep responses short, clear, and informative.
    4. **Empathy-Driven Communication:** Respond in a way that reassures the customer and builds trust.
    5. **No Off-Topic Conversations:** Keep the discussion focused on complaint resolution.

    Based on this context:  
    {context}

    Follow-up message from Human: {question}  

    Final Response only:
    """

    prompt_template = ChatPromptTemplate.from_template(template = after_rag_template)

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    llm = OllamaLLM(model=llm_name)

    chain = ConversationalRetrievalChain.from_llm(
        llm=llm, 
        memory=memory, 
        retriever=retriever, 
        combine_docs_chain_kwargs={"prompt": prompt_template}
    )

    return chain

def predict(message, history, chain):
    history_langchain_format = []
    for human, ai in history:
        history_langchain_format.append(HumanMessage(content=human))
        history_langchain_format.append(AIMessage(content=ai))
    history_langchain_format.append(HumanMessage(content=message))
    gpt_response = chain({"question": message})
    print(history_langchain_format)
    return gpt_response['answer'], chain
    
if __name__ == "__main__":

    block = gr.Blocks()

    with block:
        chain_state = gr.State(
            load_chain
        ) 
        chatbot = gr.ChatInterface(
            fn=predict,
            additional_inputs=[chain_state],
            additional_outputs=[chain_state],
            title="Chatbot"
        )

    block.launch()
