# Import dotenv package for loading .env variables
from dotenv import load_dotenv

# Initialisation
import os  # For fetching env variables
import requests, json

# from mjml import mjml_to_html
import random
import datetime
import openai

# mailjet code
from mailjet_utils import send_email_via_mailjet


load_dotenv()

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
def get_all_pages_from_database(databaseID, headers):
    query_url = f"https://api.notion.com/v1/databases/{databaseID}/query"
    res = requests.post(query_url, headers=headers)
    if res.status_code == 200:
        return res.json().get("results", [])
    else:
        return []


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


def format_pages_for_email(pages):
    email_body = "<h1>Newsletter</h1>"
    for page in pages:
        title = (
            page.get("properties", {})
            .get("title", {})
            .get("title", [{}])[0]
            .get("plain_text", "")
        )
        # Assuming a 'content' property for simplicity
        content = (
            page.get("properties", {})
            .get("content", {})
            .get("rich_text", [{}])[0]
            .get("plain_text", "")
        )
        email_body += f"<h2>{title}</h2><p>{content}</p>"
    return email_body


def notion_block_to_mjml(block):
    block_type = block.get("type")
    mjml_content = ""

    if block_type == "paragraph":
        rich_text_objects = block.get("paragraph", {}).get("rich_text", [])
        paragraph_text = ""
        for rich_text_object in rich_text_objects:
            text_content = rich_text_object.get("plain_text", "")
            link_data = rich_text_object.get("text", {}).get("link", {})
            link_url = link_data.get("url", None) if link_data is not None else None
            if link_url:
                paragraph_text += f'<a href="{link_url}">{text_content}</a>'
            else:
                paragraph_text += text_content
        mjml_content += f"<mj-text>{paragraph_text}</mj-text>"

    elif block_type == "embed":
        embed_url = block.get("embed", {}).get("url")

        # Determine the source of the embed and format the link text accordingly
        if "twitter.com" in embed_url:
            link_text = "Link to Tweet"
        elif "youtube.com" in embed_url or "youtu.be" in embed_url:
            link_text = "Link to Video"
        else:
            link_text = embed_url

        mjml_content += f'<mj-text><a href="{embed_url}">{link_text}</a></mj-text>'

    elif block_type == "image":
        image_url = block.get("image", {}).get("file", {}).get("url")
        mjml_content += f'<mj-image src="{image_url}" alt="Image"></mj-image>'

    elif block_type == "code":
        code_content = block.get("code", {}).get("text", {}).get("content", "")
        mjml_content += f"<mj-raw><pre><code>{code_content}</code></pre></mj-raw>"

    elif block_type == "bookmark":
        url = block.get("bookmark", {}).get("url", "")
        title = block.get("bookmark", {}).get("title", {}).get("content", "")
        mjml_content += f'<mj-button href="{url}">{title}</mj-button>'

    elif block_type in ["bulleted_list_item", "numbered_list_item"]:
        text_content = block.get(block_type, {}).get("text", {}).get("content", "")
        mjml_content += f"<mj-text>&bull; {text_content}</mj-text>"

    elif block_type == "to_do":
        text_content = block.get("to_do", {}).get("text", {}).get("content", "")
        mjml_content += f"<mj-text>To Do: {text_content}</mj-text>"

    elif block_type == "toggle":
        text_content = block.get("toggle", {}).get("text", {}).get("content", "")
        mjml_content += f"<mj-text>{text_content}</mj-text>"

    elif block_type in ["heading_1", "heading_2", "heading_3"]:
        level = block_type[-1]
        text_content = block.get(block_type, {}).get("text", {}).get("content", "")
        mjml_content += (
            f'<mj-text font-size="{30 - int(level)*5}px">{text_content}</mj-text>'
        )

    elif block_type == "quote":
        text_content = block.get("quote", {}).get("text", {}).get("content", "")
        mjml_content += f'<mj-text font-style="italic">{text_content}</mj-text>'

    elif block_type == "divider":
        mjml_content += "<mj-divider />"

    elif block_type == "callout":
        text_content = block.get("callout", {}).get("text", {}).get("content", "")
        mjml_content += f'<mj-text background-color="#e0e0e0">{text_content}</mj-text>'

    elif block_type == "link_preview":
        url = block.get("link_preview", {}).get("url", "")
        mjml_content += f'<mj-button href="{url}">Link Preview</mj-button>'

    return mjml_content


def notion_block_to_html(block):
    block_type = block.get("type")
    html_content = ""

    if block_type == "paragraph":
        rich_text_objects = block.get("paragraph", {}).get("rich_text", [])
        paragraph_text = ""
        for rich_text_object in rich_text_objects:
            text_content = rich_text_object.get("plain_text", "")
            link_data = rich_text_object.get("text", {}).get("link", {})
            link_url = link_data.get("url", None) if link_data is not None else None
            if link_url:
                paragraph_text += f'<a href="{link_url}">{text_content}</a>'
            else:
                paragraph_text += text_content
        html_content += f"<p>{paragraph_text}</p>"

    elif block_type == "embed":
        embed_url = block.get("embed", {}).get("url")
        if "twitter.com" in embed_url:
            link_text = "Link to Tweet"
        elif "youtube.com" in embed_url or "youtu.be" in embed_url:
            link_text = "Link to Video"
        else:
            link_text = embed_url
        html_content += f'<p><a href="{embed_url}">{link_text}</a></p>'

    elif block_type == "image":
        image_url = block.get("image", {}).get("file", {}).get("url")
        html_content += f'<img src="{image_url}" alt="Image">'

    elif block_type == "code":
        code_content = block.get("code", {}).get("text", {}).get("content", "")
        html_content += f"<pre><code>{code_content}</code></pre>"

    elif block_type == "bookmark":
        url = block.get("bookmark", {}).get("url", "")
        title = block.get("bookmark", {}).get("title", {}).get("content", "")
        html_content += f'<a href="{url}">{title}</a>'

    elif block_type in ["bulleted_list_item", "numbered_list_item"]:
        text_content = block.get(block_type, {}).get("text", {}).get("content", "")
        list_tag = "ul" if block_type == "bulleted_list_item" else "ol"
        html_content += f"<{list_tag}><li>{text_content}</li></{list_tag}>"

    elif block_type == "to_do":
        text_content = block.get("to_do", {}).get("text", {}).get("content", "")
        html_content += f"<p>To Do: {text_content}</p>"

    elif block_type == "toggle":
        text_content = block.get("toggle", {}).get("text", {}).get("content", "")
        html_content += f"<details><summary>{text_content}</summary></details>"

    elif block_type in ["heading_1", "heading_2", "heading_3"]:
        level = block_type[-1]
        text_content = block.get(block_type, {}).get("text", {}).get("content", "")
        html_content += f"<h{level}>{text_content}</h{level}>"

    elif block_type == "quote":
        text_content = block.get("quote", {}).get("text", {}).get("content", "")
        html_content += f"<blockquote>{text_content}</blockquote>"

    elif block_type == "divider":
        html_content += "<hr>"

    elif block_type == "callout":
        text_content = block.get("callout", {}).get("text", {}).get("content", "")
        html_content += f'<div style="background-color:#e0e0e0;">{text_content}</div>'

    elif block_type == "link_preview":
        url = block.get("link_preview", {}).get("url", "")
        html_content += f'<a href="{url}">Link Preview</a>'

    return html_content


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


send_newsletter(databaseID=databaseID, headers=headers)


#                 print(json.dumps(block, indent=4))
