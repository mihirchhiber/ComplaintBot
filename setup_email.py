from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from langchain.agents import tool
import os
import random
import smtplib

# Load environment variables from .env file
load_dotenv(dotenv_path=".env")

@tool
def send_voucher_email(email_to: str, email_subject: str, email_body: str):
    """Sends an email with a voucher code by taking the recipient's email, subject, and body information.
    The voucher is automatically included in the email body.
    """
    # Create an SMTP session to send the email using Gmail's SMTP server
    s = smtplib.SMTP('smtp.gmail.com', 587)
    
    # Start TLS encryption for security
    s.starttls()
    
    # Authenticate using the email and password stored in environment variables
    print(os.getenv("EMAIL_ID"), os.getenv("EMAIL_PASSWORD"))
    s.login(os.getenv("EMAIL_ID"), os.getenv("EMAIL_PASSWORD"))

    # Create the email message object
    msg = MIMEMultipart()
    msg['From'] = os.getenv("EMAIL_ID")  # Sender's email address
    msg['To'] = email_to  # Recipient's email address
    msg['Subject'] = email_subject  # Subject of the email

    # Attach the email body and add a randomly generated voucher code
    msg.attach(MIMEText(email_body + "\n\n The $5 voucher code is " + str(random.randrange(0, 99999, 1)), 'plain'))

    # Create a list of recipients (in this case, just one recipient)
    recipients = [msg['To']] 

    # Send the email
    s.sendmail(msg['From'], recipients, msg.as_string())

    # Terminate the SMTP session
    s.quit()

    return 200  # Return HTTP status code 200 to indicate success
