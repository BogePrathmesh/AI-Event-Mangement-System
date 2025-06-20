from flask import Flask, render_template, request
import os
import smtplib
import time
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import google.generativeai as genai
import schedule
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv('D:/PROGRAMMING/Event Managament/frontend/homepage/feedback form email/happen/configs.env')  # Load environment variables from .env

# Get environment variables, and raise an error if GEMINI_API_KEY is missing
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set in the .env file!")
genai.configure(api_key=gemini_api_key)

email_address = os.getenv("EMAIL_ADDRESS")
email_password = os.getenv("EMAIL_PASSWORD")

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587


def generate_email_content(event_name, recipient_name, event_details, call_to_action):
    """Generates email content using the Gemini API.

    Args:
        event_name: The name of the event.
        recipient_name: The name of the recipient.
        event_details: Details about the event.
        call_to_action: The call to action.

    Returns:
        The generated email content as a string, or an error message.
    """
    prompt = f"""
    Write a compelling email for {recipient_name} about {event_name}. Include the details: {event_details}.
    End with a strong call to action: {call_to_action}.
    """
    model = genai.GenerativeModel("models/gemini-1.5-pro-latest")
    try:
        response = model.generate_content(prompt)
        return response.text if response and response.text else "Error: Could not generate email content."
    except Exception as e:
        return f"Error generating content: {e}"


def send_email(to_email, subject, body):
    """Sends an email.

    Args:
        to_email: The recipient's email address.
        subject: The email subject.
        body: The email body.
    """
    msg = MIMEMultipart()
    msg['From'] = email_address
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(email_address, email_password)
            server.sendmail(email_address, to_email, msg.as_string())
            print(f"✅ Email sent to {to_email}")
    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {e}")



def send_bulk_emails(email_list, subject, body):
    """Sends bulk emails with a delay.

    Args:
        email_list: A list of recipient email addresses.
        subject: The email subject.
        body: The email body.
    """
    for email in email_list:
        send_email(email, subject, body)
        time.sleep(1)  # Add a 1-second delay between emails to avoid overloading the server


def schedule_bulk_emails(email_list, subject, body, send_time):
    """Schedules bulk emails to be sent at a specific time.

    Args:
        email_list: A list of recipient email addresses.
        subject: The email subject.
        body: The email body.
        send_time: The time to send the emails (e.g., "10:30").
    """

    def job():
        send_bulk_emails(email_list, subject, body)

    schedule.every().day.at(send_time).do(job)
    print(f"📅 Emails scheduled for {send_time}")



def run_scheduler():
    """Runs the scheduling loop in a separate thread."""
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check for scheduled jobs every 60 seconds



# Start the scheduler in a separate thread
threading.Thread(target=run_scheduler, daemon=True).start()



@app.route('/', methods=['GET', 'POST'])
def index():
    """Handles the main route for the web application.

    If the request method is POST, it retrieves form data, generates email content,
    and either sends the emails immediately or schedules them for later.
    If the request method is GET, it renders the index.html template.
    """
    if request.method == 'POST':
        event_name = request.form['event_name']
        recipient_name = request.form['recipient_name']
        event_details = request.form['event_details']
        call_to_action = request.form['call_to_action']
        to_emails = [email.strip() for email in request.form['to_emails'].split(',')]  # Split and strip emails
        schedule_time = request.form.get('schedule_time')

        email_body = generate_email_content(event_name, recipient_name, event_details, call_to_action)
        subject = f"You're Invited: {event_name}!"

        if schedule_time:
            schedule_bulk_emails(to_emails, subject, email_body, schedule_time)
        else:
            send_bulk_emails(to_emails, subject, email_body)

        return "Emails processed successfully!"

    return render_template("index.html")



if __name__ == '__main__':
    app.run(host="127.0.0.1", port=9010, debug=True)
