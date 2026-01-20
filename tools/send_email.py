import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email_to_manager(user_contact: str, user_question: str):
    """
    Sends an email to the manager with the user's contact details and question.
    
    Args:
        user_contact (str): The user's contact information (email or phone).
        user_question (str): The user's question or issue.
        
    Returns:
        str: A message indicating success or failure.
    """
    sender_email = os.getenv("GMAIL_USER")
    password = os.getenv("GMAIL_APP_PASSWORD")
    receiver_email = os.getenv("MANAGER_EMAIL")
    
    if not sender_email or not password or not receiver_email:
        return "Error: Email credentials or manager email not set in environment variables."

    subject = "New Inquiry from Tetkool Bot"
    body = f"""
    New inquiry received from Tetkool Bot.
    
    User Contact: {user_contact}
    
    Question/Issue:
    {user_question}
    """

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Connect to Gmail SMTP server
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.send_message(msg)
        return "Email sent successfully to the manager."
    except Exception as e:
        return f"Error sending email: {str(e)}"

# Tool definition for OpenAI
tool_definition = {
    "type": "function",
    "function": {
        "name": "send_email_to_manager",
        "description": "Send an email to the manager when the bot cannot answer a question. Requires user contact info.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_contact": {
                    "type": "string",
                    "description": "The user's contact details (email or phone number)."
                },
                "user_question": {
                    "type": "string",
                    "description": "The question or issue the user is asking about."
                }
            },
            "required": ["user_contact", "user_question"]
        }
    }
}
