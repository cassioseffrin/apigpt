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
    # Normalize unicode characters
    text = unicodedata.normalize('NFKD', text)
    # Remove diacritics
    text = text.encode('ascii', 'ignore').decode('ascii')
    # Remove special characters and replace spaces with underscores
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    text = re.sub(r'[-\s]+', '_', text)
    return text

def extract_images_from_docx(file_path):
    document = Document(file_path)
    image_data = []

    # Iterate through all the document's shapes to find images
    for shape in document.inline_shapes:
        graphic = shape._inline.graphic
        if not graphic:
            continue
        
        # Convert the graphic to XML
        graphic_xml = graphic.xml
        pic_element = ET.fromstring(graphic_xml)

        # Define XML namespaces
        namespaces = {
            'pic': 'http://schemas.openxmlformats.org/drawingml/2006/picture',
            'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
            'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
        }

        # Access the <pic:cNvPr> element within the <pic:nvPicPr>
        cNvPr_element = pic_element.find('.//pic:cNvPr', namespaces)
        if cNvPr_element is not None:
            alt_text = cNvPr_element.get('descr', None)
            if not alt_text:
                alt_text = cNvPr_element.get('name', None)
            
            if not alt_text:
                alt_text = f'image_{len(image_data) + 1}'

            image_caption = sanitize_filename(alt_text)

            # Access the <a:blip> element within the <pic:blipFill>
            blip_element = pic_element.find('.//a:blip', namespaces)
            if blip_element is not None:
                embed_id = blip_element.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')

                # Retrieve the image blob using the embed ID
                rel = document.part.rels[embed_id]
                if rel.reltype == RT.IMAGE:
                    image = rel.target_part.blob
                    image_data.append((image, alt_text, image_caption))

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
    
    # Create tables if they don't exist
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
    
    # Insert assistant with unique ID
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

    # Delete files from disk
    for (filename,) in files_to_delete:
        img_path = os.path.join(output_dir, filename)
        if os.path.exists(img_path):
            os.remove(img_path)
            print(f'Deleted image {img_path}')

    # Delete records from the database
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
        print("Usage: python extract_images.py <file_path> <assistant_id> <cleanup>")
        sys.exit(1)


#  [ "/Users/programacao/dev/gpt/src/docx/smartv4.docx" , "/Users/programacao/dev/gpt/src/docx/imgsSmart", "asst_flN0aLfDHU2Mg35WVKz0XIk1", "true" ]
 


    file_path = sys.argv[2]
    assistant_id = sys.argv[3]
    cleanup = sys.argv[4].lower() == 'true'
    output_dir = "images"
    db_path = 'images_assistant.db'

    # Setup database
    conn = setup_database(db_path)

    if cleanup:
        cleanup_files(conn, output_dir, assistant_id)
    else:
        # Extract images from the DOCX file
        image_data = extract_images_from_docx(file_path)

        # Option 1: Save images to disk
        save_images_to_disk(image_data, output_dir)

        # Option 2: Encode images to base64 and print
        # images_base64 = encode_images_to_base64(image_data)
        # print("Base64 Encoded Images:")
        # for img_caption, img_base64 in images_base64:
        #     print(f'{img_caption}: {img_base64}')
        
        # Insert image data
        insert_image_data(conn, image_data, 'default_assistant', assistant_id)
    
    conn.close()

if __name__ == "__main__":
    main()
