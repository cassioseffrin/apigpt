import sys
import os
import unicodedata
import re
from docx import Document
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.shared import Inches
import base64

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
    caption_mapping = {}

    # First pass: Map captions to their paragraph indexes
    for i, paragraph in enumerate(document.paragraphs):
        if paragraph.style.name == 'Cabeçalho 2':
            # Store the text of the paragraph with this style
            caption_mapping[i + 1] = sanitize_filename(paragraph.text)

    # Second pass: Extract images and associate with captions
    for rel in document.part.rels.values():
        if rel.reltype == RT.IMAGE:
            # Find the index of the image's paragraph
            part = rel.target_part
            image = part.blob
            para_index = None

            # Find the index of the relationship within the document
            for i, p in enumerate(document.paragraphs):
                if part.rel_type == RT.IMAGE and p._p.getparent().index(p._p) == rel._rel.idx:
                    para_index = i
                    break

            # Get the caption text from the mapping
            if para_index in caption_mapping:
                image_caption = caption_mapping[para_index]
            else:
                image_caption = f'image_{len(image_data) + 1}'

            image_data.append((image, image_caption))

    return image_data

def save_images_to_disk(image_data, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for i, (img, img_caption) in enumerate(image_data):
        img_path = os.path.join(output_dir, f'{img_caption}.png')
        with open(img_path, 'wb') as img_file:
            img_file.write(img)
        print(f'Saved image to {img_path}')

def encode_images_to_base64(image_data):
    return [(img_caption, base64.b64encode(img).decode('utf-8')) for img, img_caption in image_data]

def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_images.py <file_path> [output_dir]")
        sys.exit(1)

    file_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "images"

    image_data = extract_images_from_docx(file_path)

    # Option 1: Save images to disk
    save_images_to_disk(image_data, output_dir)

    # Option 2: Encode images to base64 and print
    images_base64 = encode_images_to_base64(image_data)
    print("Base64 Encoded Images:")
    for img_caption, img_base64 in images_base64:
        print(f
