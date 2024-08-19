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
        # Save the image stream to a temporary file
        image = Image.open(image_stream)
        temp_image_path = "temp_image.png"
        image.save(temp_image_path)

        # Set up the prompts
        system_prompt = (
            "Using the best of OCR and NLP, extract the various information fields "
            "from the image, i.e., first name, last name, email, phone, and anything "
            "else you can get."
        )
        user_prompt = (
            "Please get the following information written on the card below so I can save it in a file for later use."
        )

        # Create the chat completion request using the new API structure
        response = client.chat.completions.create(model="gpt-4-vision",  # Replace with the appropriate model name
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ])

        # Get the chat completion content
        chat_completion = response.choices[0].message.content

        return {"chatCompletion": chat_completion, "raw": response}

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
                        new_paragraph.add_run(description["chatCompletion"])
            else:
                new_paragraph.add_run(run.text)

    new_doc.save("output.docx")
    print("Images replaced with descriptions. Saved to output.docx")



replace_images_with_text("/Users/programacao/dev/gpt/src/docx/smartv5.docx")
