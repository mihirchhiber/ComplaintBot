# Food Delivery Complaint Chatbot

This project is a conversational AI chatbot built for handling food delivery complaints. The chatbot uses LangChain, RAG (Retrieval-Augmented Generation), and various tools integrated with a PostgreSQL database and email functionalities to provide personalized customer support.

## Features

- **Complaint Handling**: Efficiently processes customer complaints related to food delivery, including order status, payment issues, and late deliveries.
- **Empathetic Responses**: The chatbot communicates in a warm and empathetic tone, ensuring customers feel heard and supported.
- **Order Tracking**: Customers can inquire about the status of their orders, payment status, and delivery status using their order number.
- **Tool Integration**:
  - **Get Order Status**: Retrieves the current status of an order, including payment and delivery details.
  - **Set Human Review**: Flags an order for manual review if needed.
  - **Set Refund Status**: Initiates the refund process for problematic orders.
  - **Send Voucher Email**: Sends a voucher code to customers via email to resolve complaints or offer compensation.
  - **Retrieve Email**: Fetches the email associated with a specific order.
- **RAG Integration**: Uses Retrieval-Augmented Generation to enhance responses by retrieving relevant information from documents (e.g., company policies or rule books).
- **Conversational History**: The chatbot stores and references past interactions, allowing it to maintain context and provide relevant responses based on the ongoing conversation.
- **Dynamic Response Generation**: The chatbot uses an AI language model (e.g., Groq or Ollama) to generate responses dynamically based on the user's inquiry.
- **Database Setup**: Integration with a PostgreSQL database for order management, complaint resolution, and customer communication.

## Setup

1. Clone this repository:

   ```bash
   git clone <repository_url>
   cd <repository_directory>
   ```

2. Install the required dependencies:

   ```bash
   Copy code
   pip install -r requirements.txt
   ```


3. Create a .env file and add your environment variables for database connection, email credentials, and API keys:

   ```bash
   Copy code
   POSTGRES_PASSWORD=<your_postgres_password>
   POSTGRES_PORT=<your_postgres_port>
   EMAIL_ID=<your_email>
   EMAIL_PASSWORD=<your_email_password>
   GROQ_APIKEY=<your_groq_api_key>
   OPENAI_APIKEY=<your_openai_api_key>
   ```

4. Set up the PostgreSQL database by running the setup_db.py script:

   ```bash
   Copy code
   python setup_db.py
   ```

5. Set up email functionality (SMTP) using Gmail or another email service provider. Make sure to update the .env file with the necessary credentials.

6.Run the application:

   ```bash
   Copy code
   python main.py
   ```
7. Access the chatbot interface locally through the Gradio interface, which will open in your browser.

   
## Components
### main.py
This file contains the main logic for the chatbot, including the integration of LangChain agents, tools, and LLMs (Large Language Models). The chatbot communicates with users, handles complaints, and interacts with the database and email systems.

- Main Functions:
  - Loads the chain and sets up the LangChain agent for processing complaints.
  - Formats messages and invokes the chatbot's response generation.
  - Manages the conversation flow and history.

### setup_db.py
This file sets up the PostgreSQL database and defines functions for querying and updating order information, such as:

### Order status
- Email associated with orders
- Manual review (human check)
- Refund status
- It includes functions for connecting to the database, creating tables, and inserting sample data for testing purposes.

### setup_email.py
This file contains functions for sending voucher emails. The email includes a randomly generated voucher code to resolve customer complaints. The SMTP settings are configured to use Gmail's email server.

setup_rag.py
This file handles Retrieval-Augmented Generation (RAG) for enhanced response generation. It loads documents (e.g., company policies) and converts them into embeddings, allowing the chatbot to retrieve relevant information to respond to customer queries.

## Usage
- Chatbot Interaction: Start a conversation with the chatbot by providing details about the complaint, including the order number. The chatbot will guide the user through the complaint process.
- Response Handling: The chatbot will either provide the requested information (e.g., order status) or initiate actions such as setting the order status to "humancheck" or sending an email voucher.
- History Management: The chatbot keeps track of previous interactions, ensuring the conversation remains contextually relevant.

## Example Interaction
1. User: "My order is delayed, can you help me?"
2. Chatbot: "Please provide your order number so I can check the status."
3. User: "Order number 2743."
4. Chatbot: "Your order is marked as 'late delivery'. Would you like me to initiate a refund or set it for manual review?"

![Alt text](/screenshots/photo_6258182064180412616_y.jpg?raw=true "Optional Title")

![Alt text](/screenshots/71320b5e-dc7f-40af-907c-e15ee797aee7.jpg?raw=true "Optional Title")

![Alt text](/screenshots/photo_6258182064180412528_y.jpg?raw=true "Optional Title")

## Testing
To test the system, you can use the Gradio interface, which allows you to interact with the chatbot directly. Input test complaints or order statuses and observe how the chatbot handles different scenarios.

## Troubleshooting
Database Connection: Ensure the PostgreSQL database is running and accessible with the correct credentials.
Email Setup: If you face issues with sending emails, check the SMTP settings and ensure the email credentials are correct.
Environment Variables: Double-check that the environment variables in the .env file are correctly set.
