from openai import OpenAI
client = OpenAI()
import docx
from io import BytesIO
from PIL import Image
def get_image_description(image_stream):
    """
    Generate a description for the image using GPT.
    """
    try:
        image = Image.open(image_stream)
        temp_image_path = "temp_image.png"
        image.save(temp_image_path)
        response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
            "role": "user",
            "content": [
                {"type": "text", "text": "What’s in this image?"},
                {
                "type": "image_url",
                "image_url": {
                    "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg",
                },
                },
            ],
            }
        ],
        max_tokens=300,
        )
        print(response.choices[0])
        return response.choices[0].message.content
    except Exception as error:
        print("Error processing image:", error)
        raise error
def replace_images_with_text(doc_path):
    doc = docx.Document(doc_path)
    new_doc = docx.Document()
    for paragraph in doc.paragraphs:
        new_paragraph = new_doc.add_paragraph()
        for run in paragraph.runs:
            if run._element.xpath('.//w:drawing'):
                inline_shapes = run._element.xpath('.//w:drawing')
                for shape in inline_shapes:
                    image_data = shape.xpath('.//a:blip/@r:embed')
                    if image_data:
                        image_part = doc.part.related_parts[image_data[0]]
                        image_stream = BytesIO(image_part.blob)
                        # Get description for the image using GPT
                        description = get_image_description(image_stream)
                        # Replace the image with the description text
                        new_paragraph.add_run(description)
            else:
                new_paragraph.add_run(run.text)
    new_doc.save("output.docx")
    print("Images replaced with descriptions. Saved to output.docx")
replace_images_with_text("/Users/programacao/dev/gpt/src/docx/smartv5.docx")
