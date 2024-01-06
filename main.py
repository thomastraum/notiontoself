# Import dotenv package for loading .env variables
from dotenv import load_dotenv

# Initialisation
import os  # For fetching env variables
import requests, json

# from mjml import mjml_to_html
import random
import datetime
import openai
import logging

# mailjet code
from mailjet_utils import send_email_via_mailjet
from notion_helpers import notion_block_to_mjml, notion_block_to_html

load_dotenv()
env = os.getenv("ENV")


# Configure logging
if env == "dev":
    # logging.basicConfig(level=logging.INFO)
    logging.basicConfig(
        filename="app.log",
        filemode="a",
        format="%(asctime)s - %(message)s",
        level=logging.INFO,
    )
else:
    logging.basicConfig(level=logging.ERROR)


# Load tokens and DB IDs from .env
token = os.getenv("NOTION_TOKEN")
databaseID = os.getenv("NOTION_DATABASE_ID")

# Load Mailjet API keys for email sending
mailjet_api_key = os.getenv("MAILJET_API_KEY")
mailjet_secret_key = os.getenv("MAILJET_SECRET_KEY")

headers = {
    "Authorization": "Bearer " + token,
    "Content-Type": "application/json",
    "Notion-Version": "2022-02-22",
}

# Your existing code (functions and logic) remain unchanged


# Response a Database
def responseDatabase(databaseID, headers):
    readUrl = f"https://api.notion.com/v1/databases/{databaseID}"
    res = requests.request("GET", readUrl, headers=headers)
    print(res.status_code)


# Get all pages from a database
# def get_all_pages_from_database(databaseID, headers):
#     query_url = f"https://api.notion.com/v1/databases/{databaseID}/query"
#     res = requests.post(query_url, headers=headers)
#     if res.status_code == 200:
#         return res.json().get("results", [])
#     else:
#         return []


def get_all_pages_from_database(databaseID, headers):
    query_url = f"https://api.notion.com/v1/databases/{databaseID}/query"
    all_pages = []
    next_cursor = None

    while True:
        payload = {}
        if next_cursor:
            payload["start_cursor"] = next_cursor

        res = requests.post(query_url, headers=headers, json=payload)
        if res.status_code == 200:
            response_data = res.json()
            all_pages.extend(response_data.get("results", []))

            next_cursor = response_data.get("next_cursor")
            if not next_cursor:
                break  # Exit the loop if there are no more pages to fetch
        else:
            print(f"Failed to retrieve pages: {res.status_code}")
            break  # Exit the loop if the request fails

    return all_pages


# Get three random pages from a database
def get_three_random_pages(databaseID, headers):
    pages = get_all_pages_from_database(databaseID, headers)
    return random.sample(pages, min(3, len(pages)))


def get_page(pageId, headers):
    page_url = f"https://api.notion.com/v1/pages/{pageId}"
    res = requests.get(page_url, headers=headers)
    if res.status_code == 200:
        return res.json()
    else:
        return None


def get_blocks_of_page(page_id, headers):
    blocks = []
    next_cursor = None

    while True:
        url = f"https://api.notion.com/v1/blocks/{page_id}/children"
        if next_cursor:
            url += f"?start_cursor={next_cursor}"

        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            print(f"Failed to retrieve blocks: {res.status_code}")
            return []

        data = res.json()
        blocks.extend(data.get("results", []))

        next_cursor = data.get("next_cursor")
        if not next_cursor:
            break

    return blocks


def send_newsletter_mjml(databaseID, headers):
    # Get today's date in a formatted string, e.g., "October 14, 2023"
    today_date = datetime.datetime.today().strftime("%B %d, %Y")
    title = f"Notion To Self, Edition {today_date}"
    subject = title
    pages = get_three_random_pages(databaseID, headers)
    mjml_structure = f"""
    <mjml>
        <mj-head>
            <!-- Meta: Useful for setting the viewport on mobile devices -->
            <mj-meta name="viewport" content="width=device-width, initial-scale=1.0" />
            
            
        </mj-head>
      <mj-body>
      
        <mj-section background-color="#f0f0f0">
        <mj-column  width="600px">
            <mj-text align="center" font-size="24px" font-weight="bold">
            <h1>{title}</h1>
            </mj-text>
        </mj-column>
        </mj-section>
        <mj-section>
          <mj-column width="600px">
    """
    for page in pages:
        # Handle page-level elements here, like adding an mj-section per page
        title = (
            page.get("properties", {})
            .get("Name", {})
            .get("title", [{}])[0]
            .get("plain_text", "")
        )
        notion_page_url = page.get("url", "")
        mjml_structure += f'<mj-text font-size="20px"><h2>{title} - <a href="{notion_page_url}">Link to Page</a></h2></mj-text>'

        blocks = get_blocks_of_page(page.get("id"), headers)
        for block in blocks:
            print(json.dumps(block, indent=4))
            mjml = notion_block_to_mjml(block)
            mjml_structure += f"{mjml}"
        mjml_structure += """
          </mj-column>
        </mj-section>
        """

    mjml_structure += """
        <!-- Footer/Signature Section -->
        <mj-section background-color="#f0f0f0">
        <mj-column>
            <mj-text font-size="14px" align="center">
            Notion to Self
            </mj-text>
        </mj-column>
        </mj-section>
      </mj-body>
    </mjml>
    """

    # Convert MJML to HTML
    # html_result = mjml_to_html(mjml_structure)
    # email_body = html_result.get("html", "")

    print("sendign email")
    send_email_via_mailjet(mjml_structure, subject)

    print("mjml_structure:")
    # Save the MJML structure to a file
    with open("newsletter.mjml", "w") as mjml_file:
        mjml_file.write(mjml_structure)


def get_summary(all_html_content):
    # Summarize the HTML content using OpenAI 3.5 Turbo
    # Get the OpenAI API key from the environment variables
    summary = ""
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("Missing OpenAI API key")

    openai.api_key = openai_api_key
    try:
        # logging.info(all_html_content)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            temperature=0.0,
            top_p=1,
            messages=[
                {
                    "role": "system",
                    "content": "I want you to act as a helpful assitant. Summarize the submitted texts in less than 60 words. do not describe the HTML tags. If the text submitted is short, simply return it with minimal formatting",
                },
                {
                    "role": "user",
                    "content": f"Summarize the following in less than 60 words. do not describe the HTML tags. If the text submitted is short, simply return it without a summary:\n{all_html_content}",
                },
            ],
        )
        summary = response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        # print(f"Error: {e}")
        logging.error(f"Error get_summary: {e}")
        summary = "Summarization failed due to an error."

    return summary


def build_mjml_structure(pages):
    mjml_structure = ""
    for page in pages:
        # Handle page-level elements here, like adding an mj-section per page
        title = (
            page.get("properties", {})
            .get("Name", {})
            .get("title", [{}])[0]
            .get("plain_text", "")
        )
        notion_page_url = page.get("url", "")
        mjml_structure += f'<mj-text font-size="20px"><h2>{title} - <a href="{notion_page_url}">Link to Page</a></h2></mj-text>'

        blocks = get_blocks_of_page(page.get("id"), headers)
        # if the page only has only a couple of  block we dont need to summarize anything and can convert it
        if len(blocks) <= 20:
            for block in blocks:
                # print(json.dumps(block, indent=4))
                logging.info(f"blocks {json.dumps(block, indent=4)}")
                mjml = notion_block_to_mjml(block)
                mjml_structure += f"""
                <mj-section>
                <mj-column width="600px">
                    <mj-text font-size="16px">{mjml}</mj-text>
                </mj-column>
                </mj-section>
                """
        else:
            all_html_content = ""
            for block in blocks:
                html = notion_block_to_html(block)
                all_html_content += html

            logging.info(f"all_html_content: {all_html_content}")

            # Check if all_html_content is shorter than 6 words
            # if len(all_html_content.split()) < 30:
            #     summary = all_html_content
            # else:
            #     summary = get_summary(all_html_content)

            summary = get_summary(all_html_content)

            # Use the summarization in an MJML text tag
            mjml_structure += f"""
            <mj-section>
            <mj-column width="600px">
                <mj-text font-size="16px">{summary}</mj-text>
            </mj-column>
            </mj-section>
            """
    return mjml_structure


def send_newsletter(databaseID, headers):
    # Get today's date in a formatted string, e.g., "October 14, 2023"
    today_date = datetime.datetime.today().strftime("%B %d, %Y")
    title = f"Notion To Self, Edition {today_date}"
    subject = title
    pages = get_three_random_pages(databaseID, headers)
    mjml_structure = f"""
    <mjml>
        <mj-head>
            <!-- Meta: Useful for setting the viewport on mobile devices -->
            <mj-meta name="viewport" content="width=device-width, initial-scale=1.0" />
            
            
        </mj-head>
      <mj-body>
      
        <mj-section background-color="#f0f0f0">
        <mj-column  width="600px">
            <mj-text align="center" font-size="24px" font-weight="bold">
            <h1>{title}</h1>
            </mj-text>
        </mj-column>
        </mj-section>
    """
    mjml_structure += build_mjml_structure(pages)

    mjml_structure += """
        
        <!-- Footer/Signature Section -->
        <mj-section background-color="#f0f0f0">
        <mj-column>
            <mj-text font-size="14px" align="center">
            Notion to Self
            </mj-text>
        </mj-column>
        </mj-section>
      </mj-body>
    </mjml>
    """

    logging.info("Sending email")

    send_email_via_mailjet(mjml_structure, subject)

    if env == "dev":
        print("mjml_structure:")
        # Save the MJML structure to a file
        with open("newsletter.mjml", "w") as mjml_file:
            mjml_file.write(mjml_structure)


send_newsletter(databaseID=databaseID, headers=headers)


#                 print(json.dumps(block, indent=4))
