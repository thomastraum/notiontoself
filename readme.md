# Notes

## Notion API

how to find your database Id:

    Here's a quick procedure to find the database ID for a specific database in Notion:

    Open the database as a full page in Notion. Use the Share menu to Copy link. Now paste the link in your text editor so you can take a closer look. The URL uses the following format:

    `https://www.notion.so/{workspace_name}/{database_id}?v={view_id}`

    Find the part that corresponds to {database_id} in the URL you pasted. It is a 36 character long string. This value is your database ID.
    Note that when you receive the database ID from the API, e.g. the search endpoint, it will contain hyphens in the UUIDv4 format. You may use either the hyphenated or un-hyphenated ID when calling the API.

## OpenAI Api keys

Get them [here](https://platform.openai.com/account/api-keys)

## Env file structure

Create a file `.env` and add your details:

```

NOTION_TOKEN=<token>
NOTION_DATABASE_ID=<id>
MJ_APIKEY_PUBLIC=<api key>
MJ_APIKEY_PRIVATE=<api key private>
EMAIL_FROM=<your email>
EMAIL_SENDER_NAME=<your name>
EMAIL_TO=<your email>
OPENAI_API_KEY=<your open AI api key>
# ENV=dev #enable this for debugging 
****
```


# Install and run

```pip install -r requirements.txt```

```python main.py```

## Run with docker

1. ```docker build -t notiontoself .```
2. ```docker run notiontoself    ```

## Other

[MJML playground](https://mjml.io/try-it-live) 
