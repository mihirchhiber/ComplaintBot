from dotenv import load_dotenv
import gradio as gr
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain.schema import AIMessage, HumanMessage
from langchain_core.prompts.chat import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from langchain_ollama.llms import OllamaLLM
from langchain_openai import ChatOpenAI
import os
from setup_db import *
from setup_email import *
from setup_rag import *

# Load environment variables from .env file
load_dotenv(dotenv_path=".env")

def load_chain():
    # Define available tools for complaint handling
    tools = [get_order_status, set_humancheck_status, set_refund_status, send_voucher_email, get_email_for_order]

    # System prompt defining chatbot's role, behavior, and constraints
    system = '''
You are Charmbot, an empathetic and professional AI chatbot specializing in handling food delivery complaints efficiently. Your primary goal is to assist customers by acknowledging their concerns, gathering relevant details, and providing appropriate resolutions based on company policies. When necessary, escalate unresolved issues to a human agent.

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
2. **Strict Order Number Requirement:** Do not process any complaint without a valid order number. If missing, ask the customer using "Final Answer" instead of taking an action.
3. **Reject Assumptions:** If the customer does not provide an order number, politely ask again and do not proceed without it.
4. **Loop Until Order Number is Provided:** If missing, repeat the request and wait.
5. **Conciseness:** Keep responses short, clear, and informative.
6. **Empathy-Driven Communication:** Respond in a way that reassures the customer and builds trust.
7. **No Off-Topic Conversations:** Keep the discussion focused on complaint resolution.

You have access to the following tools:

{tools}

Use a json blob to specify a tool by providing an action key (tool name) and an action_input key (tool input).

Valid "action" values: "Final Answer" or {tool_names} ONLY

Provide only ONE action per $JSON_BLOB, as shown:

```
{{
"action": $TOOL_NAME,
"action_input": $INPUT
}}
```

Follow this format:

RAG: gives extra info relevant to question
Question: input question to answer
Thought: consider previous and subsequent steps
Acton:
```
{{
"action": $TOOL_NAME (one of the {tool_names}),
"action_input": $INPUT
}}
```
Observation: action result
... (repeat Thought/Action/Observation N times)
Thought: I know what to respond
Action:
```
{{
"action": "Final Answer",
"action_input": "response to customer"
}}

"Final Answer" is the prompt sent back to the customer so they can respond back to you.

Begin! This is a conversation, hence you should first ask the customer for missing information via "Final Answer" in action rather than using tool in action immediately. Only take an action when all required details are provided. Reminder to ALWAYS respond with a valid json blob of a single action. Use tools if necessary otherwise use "Final Answer". Respond directly if appropriate. Format is Action:```$JSON_BLOB```then Observation'''

    # Human message template with placeholders for dynamic input
    human = '''
RAG: {retriever}
Question: {input}
Thought: If necessary details (such as an order number) are missing, ask the customer using "Final Answer" in action before using tools.
{agent_scratchpad}
'''

    # Define the chat prompt template
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            MessagesPlaceholder("chat_history", optional=True),
            ("human", human),
        ]
    )
    
    # Choose the LLM model (comment/uncomment based on preference)
    llm = ChatGroq(temperature=0, groq_api_key=os.getenv('GROQ_APIKEY'), model_name="deepseek-r1-distill-llama-70b")
    # llm = OllamaLLM(model="llama3.2")
    # llm = ChatGroq(temperature=0, groq_api_key=os.getenv('GROQ_APIKEY'), model_name="mixtral-8x7b-32768")
    # llm = ChatGroq(temperature=0, groq_api_key=os.getenv('GROQ_APIKEY'), model_name="llama-3.3-70b-versatile")
    # llm = ChatOpenAI(temperature=0, model="gpt-4o", api_key=os.environ.get("OPENAI_APIKEY"))

    # Configure LLM to stop processing at certain responses
    llm_with_stop = llm.bind(stop=["\nFinal Answer", "\nNone"])

    # Create a structured chat agent
    agent = create_structured_chat_agent(llm_with_stop, tools, prompt)

    # Define agent executor settings
    chain = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=100,
    )

    return chain

def predict(message, history, chain):
    # Format chat history into LangChain message format
    history_langchain_format = []
    for human, ai in history:
        history_langchain_format.append(HumanMessage(content=human))
        history_langchain_format.append(AIMessage(content=ai))
    history_langchain_format.append(HumanMessage(content=message))

    # Invoke the chatbot and get a response
    response = chain.invoke({
        "input": message,
        "chat_history": history_langchain_format,
        "retriever": get_rag(message)
    })
    print("Agent:", response['output'])
    return response['output'], chain

if __name__ == "__main__":
    # Initialize Gradio interface
    block = gr.Blocks()

    with block:
        chain_state = gr.State(load_chain)
        chatbot = gr.ChatInterface(
            fn=predict,
            additional_inputs=[chain_state],
            additional_outputs=[chain_state],
            title="Food Delivery Complaint Chatbot"
        )

    # Launch Gradio app
    block.launch()

    # Uncomment below if you want a shareable link
    # block.launch(share=True)