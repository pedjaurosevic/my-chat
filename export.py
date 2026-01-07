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


def export_chat_to_epub(messages, filename):
    """Export chat to EPUB format"""
    try:
        from ebooklib import epub

        book = epub.EpubBook()

        book.set_identifier(filename.replace('.epub', ''))
        book.set_title('OLLAMA.CORE Chat')
        book.set_language('en')

        style = '''
        @namespace epub "http://www.idpf.org/2007/ops";
        body { font-family: serif; }
        p { margin: 0.5em 0; text-align: justify; }
        h1 { text-align: center; margin: 1em 0; }
        h2 { color: #333; margin: 1em 0 0.5em 0; }
        .user { background-color: #f0f0f0; padding: 10px; margin: 10px 0; border-radius: 5px; }
        .assistant { background-color: #e8f4f8; padding: 10px; margin: 10px 0; border-radius: 5px; }
        .model { color: #666; font-size: 0.9em; font-style: italic; }
        .separator { border-top: 1px solid #ccc; margin: 20px 0; }
        '''
        nav_css = epub.EpubItem(
            uid="style_nav",
            file_name="style/nav.css",
            media_type="text/css",
            content=style
        )
        book.add_item(nav_css)

        chapters = []

        for i, msg in enumerate(messages):
            if msg["role"] == "system":
                continue

            content = msg['content'].replace('\n', '<br/>')
            model = msg.get('model_name', '')
            role = msg["role"].upper()

            if msg["role"] == "user":
                html_content = f'''
                <h2>[{role}]</h2>
                <div class="user">{content}</div>
                '''
            else:
                html_content = f'''
                <h2>[{role}]</h2>
                <div class="model">Model: {model}</div>
                <div class="assistant">{content}</div>
                '''

            chapter = epub.EpubHtml(
                title=f'{role} {i+1}',
                file_name=f'chap_{i+1}.xhtml',
                lang='en'
            )
            chapter.content = html_content
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
                self.set_font('Helvetica', 'B', 12)
                self.cell(0, 10, 'OLLAMA.CORE Chat', 0, 1, 'C')
                self.ln(5)

            def footer(self):
                self.set_y(-15)
                self.set_font('Helvetica', 'I', 8)
                self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

        pdf = PDF()
        pdf.add_page()
        pdf.set_font('Helvetica', '', 11)

        for msg in messages:
            if msg["role"] == "system":
                continue

            role = msg["role"].upper()
            model = msg.get('model_name', '')
            content = msg['content']

            if msg["role"] == "user":
                pdf.set_font('Helvetica', 'B', 12)
                pdf.cell(0, 8, f"[{role}]", 0, 1)
                pdf.set_font('Helvetica', '', 11)
            else:
                pdf.set_font('Helvetica', 'B', 12)
                pdf.cell(0, 8, f"[{role}]", 0, 1)
                pdf.set_font('Helvetica', 'I', 9)
                pdf.cell(0, 6, f"Model: {model}", 0, 1)
                pdf.set_font('Helvetica', '', 11)

            lines = content.split('\n')
            for line in lines:
                pdf.multi_cell(0, 6, line)

            pdf.ln(5)

            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(5)

        pdf.output(filename)
        return True
    except Exception as e:
        return False
