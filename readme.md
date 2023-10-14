https://www.notion.so/thomastraum/1add8aa010a5403eb9ea2d7c627a06f2?v=dda9197e3c064bc5824598a6b93de776&pvs=4

Here's a quick procedure to find the database ID for a specific database in Notion:

Open the database as a full page in Notion. Use the Share menu to Copy link. Now paste the link in your text editor so you can take a closer look. The URL uses the following format:

https://www.notion.so/{workspace_name}/{database_id}?v={view_id}
Find the part that corresponds to {database_id} in the URL you pasted. It is a 36 character long string. This value is your database ID.
Note that when you receive the database ID from the API, e.g. the search endpoint, it will contain hyphens in the UUIDv4 format. You may use either the hyphenated or un-hyphenated ID when calling the API.

https://mjml.io/try-it-live
