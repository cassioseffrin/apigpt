import sys
import os
import unicodedata
import re
import sqlite3
from docx import Document
from docx.opc.constants import RELATIONSHIP_TYPE as RT
import base64
from xml.etree import ElementTree as ET
def sanitize_filename(text):
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    text = re.sub(r'[-\s]+', '_', text)
    return text
def extract_images_from_docx(file_path):
    document = Document(file_path)
    image_data = []
    image_counter = 1
    for shape in document.inline_shapes:
        graphic = shape._inline.graphic
        if not graphic:
            continue
        graphic_xml = graphic.xml
        pic_element = ET.fromstring(graphic_xml)
        namespaces = {
            'pic': 'http://schemas.openxmlformats.org/drawingml/2006/picture',
            'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
            'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
        }
        cNvPr_element = pic_element.find('.//pic:cNvPr', namespaces)
        if cNvPr_element is not None:
            alt_text = cNvPr_element.get('descr', None)
            if not alt_text:
                alt_text = cNvPr_element.get('name', None)
            if not alt_text:
                alt_text = f'image_{image_counter:04d}'
            filename = f'image_{image_counter:04d}' 
            image_counter += 1
            blip_element = pic_element.find('.//a:blip', namespaces)
            if blip_element is not None:
                embed_id = blip_element.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
                rel = document.part.rels[embed_id]
                if rel.reltype == RT.IMAGE:
                    image = rel.target_part.blob
                    image_data.append((image, alt_text, filename))
    return image_data
def save_images_to_disk(image_data, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    for i, (img, img_desc, img_caption) in enumerate(image_data):
        img_path = os.path.join(output_dir, f'{img_caption}.png')
        with open(img_path, 'wb') as img_file:
            img_file.write(img)
        print(f'Saved image to {img_path}')
def encode_images_to_base64(image_data):
    return [(img_caption, base64.b64encode(img).decode('utf-8')) for img, img_desc, img_caption in image_data]
def setup_database(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS assistant (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            assistantId TEXT UNIQUE NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS images (
            filename TEXT NOT NULL,
            description TEXT,
            assistant_id INTEGER,
            FOREIGN KEY (assistant_id) REFERENCES assistant(id)
        )
    ''')
    conn.commit()
    return conn
def insert_image_data(conn, image_data, assistant_name, assistant_id):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO assistant (name, assistantId) VALUES (?, ?)
    ''', (assistant_name, assistant_id))
    cursor.execute('''
        SELECT id FROM assistant WHERE assistantId = ?
    ''', (assistant_id,))
    assistant_row_id = cursor.fetchone()[0]
    for img, img_desc, img_caption in image_data:
        cursor.execute('''
            INSERT INTO images (filename, description, assistant_id) VALUES (?, ?, ?)
        ''', (f'{img_caption}.png', img_desc, assistant_row_id))
    conn.commit()
def cleanup_files(conn, output_dir, assistant_id):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT images.filename FROM images
        JOIN assistant ON images.assistant_id = assistant.id
        WHERE assistant.assistantId = ?
    ''', (assistant_id,))
    files_to_delete = cursor.fetchall()
    for (filename,) in files_to_delete:
        img_path = os.path.join(output_dir, filename)
        if os.path.exists(img_path):
            os.remove(img_path)
            print(f'Deleted image {img_path}')
    cursor.execute('''
        DELETE FROM images
        WHERE assistant_id = (SELECT id FROM assistant WHERE assistantId = ?)
    ''', (assistant_id,))
    cursor.execute('''
        DELETE FROM assistant WHERE assistantId = ?
    ''', (assistant_id,))
    conn.commit()
def main():
    if len(sys.argv) < 4:
        print("Usage: python extract_images.py <file_path> <output_dir> <assistant_id> <cleanup>")
        sys.exit(1)
    file_path = sys.argv[1]
    output_dir = sys.argv[2]
    assistant_id = sys.argv[3]
    cleanup = sys.argv[4].lower() == 'true'
    db_path = 'images_assistant.db'
    conn = setup_database(db_path)
    if cleanup:
        cleanup_files(conn, output_dir, assistant_id)
    image_data = extract_images_from_docx(file_path)
    save_images_to_disk(image_data, output_dir)
    insert_image_data(conn, image_data, 'default_assistant', assistant_id)
    conn.close()
if __name__ == "__main__":
    main()
