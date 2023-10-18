
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
        
        rich_text_objects = block.get("code", {}).get("rich_text", [])
        for rich_text_object in rich_text_objects:
            code_content = rich_text_object.get("plain_text", "")
 
        # code_content = block.get("code", {}).get("rich_text").get("text", {}).get("content")

        mjml_content += f"<mj-raw><pre><code>{code_content}</code></pre></mj-raw>"

    elif block_type == "bookmark":
        url = block.get("bookmark", {}).get("url", "")
        title = block.get("bookmark", {}).get("title", {}).get("content", "")
        mjml_content += f'<mj-button href="{url}">Link: {title}</mj-button>'

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
        rich_text_objects = block.get("quote", {}).get("rich_text", [])
        for rich_text_object in rich_text_objects:
            text_content = rich_text_object.get("plain_text", "")
 
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
