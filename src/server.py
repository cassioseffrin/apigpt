from flask import Flask, request, jsonify
import os
import openai
import sqlite3
import base64
from extract_images import extract_images_from_docx, encode_images_to_base64
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

app = Flask(__name__)
openai.api_key = OPENAI_API_KEY


def create_new_thread_and_talk(message):
    thread = openai.beta.threads.create(
        messages=[
            {
                'role': 'user',
                'content': message,
            }
        ]
    )
    return thread


@app.route('/startThreadAndTalk', methods=['POST'])
def start_thread_and_talk():
    try:
        data = request.get_json()
        message = data['message']
        thread = create_new_thread_and_talk(message)
        assistant_id = "asst_flN0aLfDHU2Mg35WVKz0XIk1"
        response = continuar_conversar(thread.id, assistant_id, message)
        response = {'threadId': thread.id, **response}
        return jsonify(response), 200
    except Exception as e:
        print(f"Error: {e}")
        return "Error", 500


def create_new_thread():
    return openai.beta.threads.create()


@app.route('/createNewThread', methods=['GET'])
def create_new_thread_endpoint():
    try:
        thread = create_new_thread()
        return jsonify({'threadId': thread.id if thread else None}), 200
    except Exception as e:
        print(f"Error: {e}")
        return "Error creating thread", 500



@app.route('/chat', methods=['POST'])
def chat():
    try:
        assistant_id = "asst_flN0aLfDHU2Mg35WVKz0XIk1"
        data = request.get_json()
        thread_id = data['threadId']
        message = data['message']
        
        
        openai.beta.threads.messages.create(
            thread_id=thread_id,
            role='user',
            content=message
        )
        
        
        response = continuar_conversar(thread_id, assistant_id, message)
        if response:
            
            image_references = []
            for content_block in response.get('content', []):
                if 'source' in content_block:
                    image_references.append(content_block)
            
            if image_references:
                
                base64_images = {}
                for ref in image_references:
                    
                    description = ref
                    images_base64 = get_images_base64(message)
                    base64_images.update(images_base64)
                
                
                response['images'] = base64_images

        return jsonify(response), 200
    except Exception as error:
        print(f"Error: {error}")
        return "Internal Server Error", 500


@app.route('/webhookBitrix', methods=['POST'])
def webhook_bitrix():
    try:
        data = request.get_json()
        prompt = data['prompt']
        assistant_id = "asst_flN0aLfDHU2Mg35WVKz0XIk1"
        thread = create_new_thread()
        response = conversar_nova_thread_bitrix(thread.id, assistant_id, prompt)
        return jsonify(response), 200
    except Exception as e:
        print(f"Error: {e}")
        return "Internal Server Error", 500


def conversar_nova_thread_bitrix(thread_id, assistant_id, message):
    openai.beta.threads.messages.create(
        thread_id=thread_id,  
        role='user',
        content=message
    )
    run = openai.beta.threads.runs.create_and_poll(
        thread_id=thread_id,  
        assistant_id=assistant_id
    )
    if run.status == 'completed':
        messages = openai.beta.threads.messages.list(thread_id)
        return [message_to_dict(msg) for msg in messages]
    else:
        return None


def conversar(thread_id, assistant_id):
    messages = process_messages(thread_id, assistant_id)
    if messages:
        for message in messages:
            print(message)
            return message_to_dict(message)  
    else:
        return None




def continuar_conversar(thread_id, assistant_id, message):
    openai.beta.threads.messages.create(
        thread_id=thread_id,  
        role='user',
        content=message
    )

    run = openai.beta.threads.runs.create_and_poll(
        thread_id=thread_id,  
        assistant_id=assistant_id
    )

    if run.status == 'completed':
        messages = openai.beta.threads.messages.list(thread_id)
        if messages:
            last_message = messages.data[0]  
            print(last_message)
            return message_to_dict(last_message)  
    return None


def process_messages(thread_id, assistant_id):
    run = openai.beta.threads.runs.create_and_poll(
        thread_id=thread_id,  
        assistant_id=assistant_id,
        additional_instructions=''
    )
    print(f"Processamento finalizado: {run.status}")
    if run.status == 'completed':
        messages = openai.beta.threads.messages.list(thread_id)
        return [message_to_dict(message) for message in messages]
    return None


def message_to_dict(message):
    return {
        'id': message.id,
        'role': message.role,
        'content': [block.text.value for block in message.content],
        'created_at': message.created_at,
        'thread_id': message.thread_id
    }



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
        with open(os.path.join('/Users/programacao/dev/gpt/src/docx/imgsSmart', filename), 'rb') as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
            images_base64[filename] = img_base64

    conn.close()
    return images_base64


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4014)
