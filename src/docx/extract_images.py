import sys
import os
import unicodedata
import re
from docx import Document
from docx.opc.constants import RELATIONSHIP_TYPE as RT
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

    # Iterate through all the document's shapes to find images
    for shape in document.inline_shapes:
        graphic = getattr(shape, '_inline', None)
        if graphic:
            graphic_data = getattr(graphic, 'graphic', None)
            if graphic_data:
                pic = getattr(graphic_data.graphicData, 'pic', None)
                if pic:
                    blip_fill = getattr(pic, 'blipFill', None)
                    if blip_fill:
                        blip = getattr(blip_fill.blip, 'embed', None)
                        if blip:
                            # Access the relationship part for the image
                            rel = document.part.rels[blip]
                            if rel.reltype == RT.IMAGE:
                                # Extract image blob
                                image = rel.target_part.blob

                                # Get the alt text or name of the image
                                cNvPr = getattr(pic.nvPicPr.cNvPr, 'descr', None)
                                name = getattr(pic.nvPicPr.cNvPr, 'name', None)

                                # Use alt text if available, otherwise use name
                                alt_text = cNvPr if cNvPr else name

                                # Check if alt_text or name is available
                                if alt_text:
                                    image_caption = sanitize_filename(alt_text)
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
        print(f'{img_caption}: {img_base64}')

if __name__ == "__main__":
    main()
