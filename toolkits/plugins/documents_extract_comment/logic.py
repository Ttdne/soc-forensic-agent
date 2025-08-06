import os
from zipfile import ZipFile
import xml.etree.ElementTree as ET
import time
import openpyxl

def extract_comments_from_embedded_excel(docx, embedded_file):
    comments_dict = {}
    with docx.open(embedded_file) as file:
        wb = openpyxl.load_workbook(file, data_only=True)
        for sheet in wb.sheetnames:
            worksheet = wb[sheet]
            for cell in worksheet._cells.values():
                if cell.comment:
                    # Lưu nội dung của ô cùng với comment
                    comments_dict[cell.value.split('{{')[1].split('}}')[0]] = cell.comment.text
    return comments_dict

def extract_comments_and_text_from_docx(file_path):
    comments_dict = {}

    with ZipFile(file_path, 'r') as docx:
        try:
            # Đọc các file XML cần thiết
            comments_xml = docx.read('word/comments.xml')
            document_xml = docx.read('word/document.xml')
        except KeyError:
            print("No comments.xml or document.xml file found in the .docx archive.")
            return comments_dict

        comments_tree = ET.fromstring(comments_xml)
        document_tree = ET.fromstring(document_xml)

        w_namespace = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

        # Parse comments to map comment IDs to text
        comments = {}
        for comment in comments_tree.findall('w:comment', namespaces=w_namespace):
            comment_id = comment.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}id')
            comment_text = ''.join(comment.itertext()).strip()
            comments[comment_id] = comment_text

        # Create a map from comment ID to the actual text in the document
        comment_ranges = {}
        for elem in document_tree.iter():
            if elem.tag.endswith('commentRangeStart'):
                comment_id = elem.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}id')
                comment_ranges[comment_id] = []

            if elem.tag.endswith('commentRangeEnd'):
                comment_id = elem.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}id')
                if comment_id in comment_ranges:
                    highlighted_text = ''.join(filter(None, comment_ranges[comment_id])).strip()
                    if highlighted_text:
                        comments_dict[highlighted_text] = comments.get(comment_id, '')

            if elem.tag.endswith('t'):
                for comment_id in comment_ranges:
                    if comment_ranges[comment_id] is not None:
                        comment_ranges[comment_id].append(elem.text)

        # Extract comments from all embedded Excel files
        embedded_files = [name for name in docx.namelist() if name.startswith('word/embeddings/')]
        for embedded_file in embedded_files:
            if embedded_file.endswith('.xlsx'):
                excel_comments = extract_comments_from_embedded_excel(docx, embedded_file)
                comments_dict.update(excel_comments)

    return comments_dict

def process_word_file(file_path):
    comments = extract_comments_and_text_from_docx(file_path)
    return comments

def execute(file_path: str, state_dir: str = None, **kwargs):
    try:
        if state_dir is None:
            timestamp = str(int(time.time()))
            state_dir = os.path.join("./test_environment", timestamp)
            os.makedirs(state_dir, exist_ok=True)

        if not file_path.startswith(state_dir):
            file_path = os.path.normpath(file_path).lstrip(os.sep)
            full_file_path = os.path.join(state_dir, file_path)
        else:
            full_file_path = file_path

        if not os.path.exists(full_file_path):
            return {
                "tool": "comments_process",
                "success": False,
                "error": f"{file_path} không tồn tại"
            }

        comments = process_word_file(full_file_path)
        return {
            "tool": "comments_process",
            "success": True,
            "comments": comments
        }
    except Exception as e:
        return {
            "tool": "comments_process",
            "success": False,
            "error": str(e)
        }