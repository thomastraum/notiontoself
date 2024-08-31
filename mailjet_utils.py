import os
import requests
from pprint import pprint
import logging


def send_email_via_mailjet(mjml_structure, subject=""):
    # Fetch API keys and emails from environment variables
    mailjet_api_key = os.getenv("MJ_APIKEY_PUBLIC")
    mailjet_secret_key = os.getenv("MJ_APIKEY_PRIVATE")
    email_from = os.getenv("EMAIL_FROM")
    sender_name = os.getenv("EMAIL_SENDER_NAME")
    email_to = os.getenv("EMAIL_TO")
    env = os.getenv("ENV")

    # API settings
    url = "https://api.mailjet.com/v3.1/send"
    auth = (mailjet_api_key, mailjet_secret_key)
    headers = {"Content-Type": "application/json"}

    # Check for missing environment variables
    if not all(
        [mailjet_api_key, mailjet_secret_key, email_from, sender_name, email_to]
    ):
        print("Missing environment variables. Check your setup.")
        return 400

    # Compose payload
    payload = {
        "Messages": [
            {
                "From": {"Email": email_from, "Name": sender_name},
                "To": [{"Email": email_to, "Name": "Recipient"}],
                "Subject": subject,
                "Mj-TemplateLanguage": True,
                "HTMLPart": mjml_structure,
            }
        ]
    }

    # Perform API call
    response = requests.post(url, auth=auth, headers=headers, json=payload)

    if env == "dev":
        # print(f"Email payload: {payload}")
        pprint(response.json())
        logging.info(f"mailjet response: {response.json()}")

    if response.status_code == 200:
        print("Email sent successfully")
    else:
        print(f"Failed to send email: {response.content}")
        return response.status_code
