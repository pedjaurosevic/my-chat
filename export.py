"""
Export funkcionalnost za chat razgovore
"""

import time
import os
from io import BytesIO


def export_chat_to_text(messages):
    """Export chat to plain text format"""
    text = "=" * 60 + "\n"
    text += f"OLLAMA.CORE - Chat Export\n"
    text += f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
    text += f"Total messages: {len([m for m in messages if m['role'] != 'system'])}\n"
    text += "=" * 60 + "\n\n"

    for msg in messages:
        if msg["role"] == "system":
            continue

        role = msg["role"].upper()
        model = msg.get("model_name", "")

        if msg["role"] == "user":
            text += f"[{role}]\n"
        else:
            text += f"[{role} - {model}]\n"

        text += f"{msg['content']}\n"
        text += "-" * 40 + "\n\n"

        return text


def export_chat_to_html(messages):
    """Export chat to HTML format (for PDF/EPUB)"""
    html = (
        """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>OLLAMA.CORE Chat</title>
    <style>
        body {
            font-family: 'Georgia', serif;
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
            line-height: 1.6;
            background-color: #f5f5f5;
        }
        .user {
            background-color: #e8e8e8;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
        }
        .assistant {
            background-color: #e8f4e8;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
        }
        .meta {
            font-size: 11px;
            color: #666;
            margin-bottom: 5px;
        }
        .message {
            margin: 0;
            padding: 10px;
        }
    </style>
</head>
<body>
    <h1 style="text-align: center;">OLLAMA.CORE Chat</h1>
    <p style="text-align: center;">Date: """
        + time.strftime("%Y-%m-%d %H:%M:%S")
        + """</p>
    <hr style="margin: 20px 0;">
"""
    )

    for msg in messages:
        if msg["role"] == "system":
            continue

        role = msg["role"].upper()
        model = msg.get("model_name", "")

        if msg["role"] == "user":
            css_class = "user"
        else:
            css_class = "assistant"

        html += f"""
    <div class="{css_class}">
        <div class="meta">Role: {role} | Model: {model}</div>
        <div class="message">{msg["content"]}</div>
    </div>
"""

    html += """
</body>
</html>
"""

    return html


def export_chat_to_epub(messages, filename):
    """Export chat to EPUB format"""
    try:
        from ebooklib import epub

        book = epub.EpubBook()
        book.set_identifier(filename.replace(".epub", ""))
        book.set_title("OLLAMA.CORE Chat")
        book.set_language("en")

        style = """
            @namespace epub "http://www.idpf.org/2007/ops";
            body { font-family: serif; }
            p { margin: 0.5em 0; text-align: justify; }
            h1 { text-align: center; margin: 1em 0; }
            h2 { color: #333; margin: 1em 0 0.5em 0; }
            .user { background-color: #e8e8e8; padding: 10px; margin: 10px 0; border-radius: 5px; }
            .assistant { background-color: #e8f4f8; padding: 10px; margin: 10px 0; border-radius: 5px; }
            .model { color: #666; font-size: 0.9em; font-style: italic; }
            .meta { font-size: 11px; color: #666; margin-bottom: 5px; }
        """

        nav_css = epub.EpubItem(
            uid="style_nav",
            file_name="style/nav.css",
            media_type="text/css",
            content=style,
        )
        book.add_item(nav_css)

        # Generate HTML using export_chat_to_html
        html_content = export_chat_to_html(messages)

        # Create chapters from HTML
        start_tag = "<body>"
        end_tag = "</body>"

        # Extract messages from HTML
        import re

        msg_matches = re.findall(
            r'<div class="(user|assistant)">\s*<div class="meta">Role: (?:USER|ASSISTANT)[^<]*</div>\s*<div class="message">(.*?)</div>',
            html_content,
        )

        for i, (css_class, role_model, msg_content) in enumerate(msg_matches, 1):
            title = f"Message {i}"
            html_chapter = f"""
            <?xml version="1.0" encoding="UTF-8"?>
<chapter>
  <title>{title}</title>
  <h1>{role}</h1>
  <h2>{role_model}</h2>
  <p>{msg_content}</p>
</chapter>
"""
            chapter = epub.EpubHtml(
                title=f"{role} {i + 1}", file_name=f"chap_{i + 1}.xhtml", lang="en"
            )
            chapter.content = html_chapter
            chapter.add_item(nav_css)
            book.add_item(chapter)
            chapters.append(chapter)

        book.toc = chapters
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        epub.write_epub(filename, book, {})
        return True
    except Exception as e:
        return False


def export_chat_to_pdf(messages, filename):
    """Export chat to PDF format"""
    try:
        from fpdf import FPDF

        class PDF(FPDF):
            def header(self):
                self.set_font("Helvetica", "B", 12)
                self.cell(0, 10, "OLLAMA.CORE Chat", 0, 1, "C")
                self.ln(5)

            def footer(self):
                self.set_y(-15)
                self.set_font("Helvetica", "I", 8)
                self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")

        pdf = PDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "", 11)

        for msg in messages:
            if msg["role"] == "system":
                continue

            role = msg["role"].upper()
            model = msg.get("model_name", "")
            content = msg["content"]

            if msg["role"] == "user":
                pdf.set_font("Helvetica", "B", 12)
                pdf.cell(0, 8, f"[{role}]", 0, 1)
                pdf.set_font("Helvetica", "", 11)
            else:
                pdf.set_font("Helvetica", "B", 12)
                pdf.cell(0, 8, f"[{role}]", 0, 1)
                pdf.set_font("Helvetica", "I", 9)
                pdf.cell(0, 6, f"Model: {model}", 0, 1)
                pdf.set_font("Helvetica", "", 11)

            lines = content.split("\n")
            for line in lines:
                pdf.multi_cell(0, 6, line)

            pdf.ln(5)

            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(5)

        pdf.output(filename)
        return True
    except Exception as e:
        return False
