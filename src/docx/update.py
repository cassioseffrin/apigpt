from flask import Flask, request, jsonify
import os
import openai
import sqlite3
import base64
from extract_images import extract_images_from_docx, encode_images_to_base64

# Load environment variables from a .env file
from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

app = Flask(__name__)
openai.api_key = OPENAI_API_KEY

# Initialize OpenAI client
client = openai.Client(api_key=OPENAI_API_KEY)

# Function to convert message to dict
def message_to_dict(message):
    return {
        'id': message.id,
        'content': [block.text.value for block in message.content if block.type == 'text'],
        'role': message.role
    }

# Function to get image base64 from the database
def get_images_base64(description):
    db_path = 'images_assistant.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT filename FROM images
        WHERE description LIKE ?
    ''', (f'%{description}%',))

    filenames = cursor.fetchall()
    images_base64 = {}
    
    for (filename,) in filenames:
        with open(os.path.join('output_dir', filename), 'rb') as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
            images_base64[filename] = img_base64

    conn.close()
    return images_base64

# Endpoint to chat
@app.route('/chat', methods=['POST'])
def chat():
    try:
        assistant_id = "asst_flN0aLfDHU2Mg35WVKz0XIk1"
        data = request.get_json()
        thread_id = data['threadId']
        message = data['message']
        
        # Create a message in the thread
        openai.beta.threads.messages.create(
            thread_id=thread_id,
            role='user',
            content=message
        )
        
        # Process and respond
        response = continuar_conversar(thread_id, assistant_id, message)
        
        if response:
            # Check if the response contains references to images
            image_references = []
            for content_block in response.get('content', []):
                if 'source' in content_block:
                    image_references.append(content_block)
            
            if image_references:
                # For each image reference, get the base64-encoded image
                base64_images = {}
                for ref in image_references:
                    description = ref.get('description', '')
                    images_base64 = get_images_base64(description)
                    base64_images.update(images_base64)
                
                # Add base64 image data to response
                response['images'] = base64_images

        return jsonify(response), 200
    except Exception as error:
        print(f"Error: {error}")
        return "Internal Server Error", 500

# Function definitions for continuar_conversar and other parts of your code go here

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4014)
