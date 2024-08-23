from datetime import datetime
import json
from flask import Flask, jsonify, request, send_from_directory 
import os
import openai
import sqlite3
import base64
from extract_images_desc_inside_image import extract_images_from_docx, encode_images_to_base64
from dotenv import load_dotenv
import re
from fuzzywuzzy import fuzz
from openai import OpenAI
client = OpenAI()
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
app = Flask(__name__)
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
        # openai.beta.threads.messages.create(
        #     thread_id=thread_id,
        #     role='user',
        #     content=message
        # )
        response = continuar_conversar(thread_id, assistant_id, message)
        if response:
            image_references = []
            for content_block in response.get('content', []):
                if 'source' in content_block:
                    image_references.append(content_block)
            if image_references:
                url_images = {}
                for ref in image_references:
                    description = ref
                    images_urls = get_images_urls(message)
                    url_images.update(images_urls)
                response['images'] = url_images
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
def get_delivery_date(order_id: str) -> datetime:
    # Connect to the database
    # conn = sqlite3.connect('ecommerce.db')
    # cursor = conn.cursor()
    # ...        
    return datetime.now()   
def continuar_conversar_old(thread_id, assistant_id, message):
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
import json

def continuar_conversar(thread_id, assistant_id, message):
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_delivery_date",
                "description": "Get the delivery date for a customer's order. Call this whenever you need to know the delivery date, for example when a customer asks 'Where is my package?'",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "order_id": {
                            "type": "string",
                            "description": "The customer's order ID."
                        }
                    },
                    "required": ["order_id"],
                    "additionalProperties": False
                }
            }
        }
    ]
    
    messages = []
    messages.append({"role": "system", "content": "You are a helpful customer support assistant. Use the supplied tools to assist the user."})
    messages.append({"role": "user", "content": message})
    
    response = client.chat.completions.create(
        model='gpt-4o',
        messages=messages,
        tools=tools
    )
    
    tool_call = response.choices[0].message.tool_calls 
    
    if tool_call:
        arguments = json.loads(tool_call[0].function.arguments)
        order_id = arguments.get('order_id')
        
        if order_id:
            delivery_date = get_delivery_date(order_id)
            data = delivery_date.strftime('%Y-%m-%d %H:%M:%S')
            print(delivery_date)
            
            function_call_result_message = {
                "role": "tool",
                "content": json.dumps({
                    "order_id": order_id,
                    "delivery_date": data
                }),
                "tool_call_id": tool_call[0].id
            }
            print(function_call_result_message)
            #  I think it is order_12345, could you estimate the delivery date?
            completion_payload = {
                "model": "gpt-4o",
                "messages": [
                    {"role": "system", "content": "You are a helpful customer support assistant. Use the supplied tools to assist the user."},
                    {"role": "user", "content": "Hi, can you tell me the delivery date for my order?"},
                    {"role": "assistant", "content": "Hi there! I can help with that. Can you please provide your order ID?"},
                    {"role": "user", "content": "I think it is order_12345"},
                    response.choices[0].message,
                    function_call_result_message
                ]
            }
            
            response = openai.chat.completions.create(
                model=completion_payload["model"],
                messages=completion_payload["messages"]
            )
            
            msg = response.choices[0].message
            
            return {
                'id': response.id,
                'role': 'assistant',
                'content': [msg.content],
                'created_at': response.created,
                'thread_id': thread_id
            }
    

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
    image_counter = 0
    for (filename,) in filenames:
        with open(os.path.join('/Users/programacao/dev/gpt/src/docx/imgsSmart', filename), 'rb') as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
            image_counter += 1
            image = f'image_{image_counter:04d}' 
            images_base64[image] = img_base64
    conn.close()
    return images_base64
# def get_images_urls(description):
#     db_path = 'images_assistant.db'
#     conn = sqlite3.connect(db_path)
#     cursor = conn.cursor()
#     cursor.execute('''
#         SELECT filename FROM images
#         WHERE description LIKE ?
#     ''', (f'%{description}%',))
#     filenames = cursor.fetchall()
#     images_urls = {}
#     image_counter = 0
#     for (filename,) in filenames:
#         image_counter += 1
#         image = f'image_{image_counter:04d}'
#         images_urls[image] = f'/api/images/{filename}'
#     conn.close()
#     return images_urls
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'\W+', ' ', text)
    return text.strip()
def custom_match_score(description, desc):
    if description in desc:
        return 100
    return fuzz.token_sort_ratio(description, desc)
def get_images_urls(description, threshold=90, max_results=5):
    db_path = 'images_assistant.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT description, filename FROM images')
    rows = cursor.fetchall()
    preprocessed_description = preprocess_text(description)
    matched_images = []
    for desc, filename in rows:
        preprocessed_desc = preprocess_text(desc)
        match_score = custom_match_score(preprocessed_description, preprocessed_desc)
        if match_score >= threshold:
            matched_images.append((filename, match_score))
    matched_images.sort(key=lambda x: x[1], reverse=True)
    top_images = matched_images[:max_results]
    if not top_images:
        return {}
    images_json = {}
    image_counter = 0
    for filename, match_score in top_images:
        image_counter += 1
        image_key = f'image_{image_counter:04d}'
        images_json[image_key] = {
            'url': f'/api/images/{filename}',
            'match_score': match_score
        }
    conn.close()
    return images_json
@app.route('/api/images/<filename>')
def get_image(filename):
    image_directory = './docx/imgsSmart/'
    try:
        return send_from_directory(image_directory, filename)
    except FileNotFoundError:
        return "Image not found", 404
# http://localhost:5000/api/getTempImage/temp_image_rId8.png    
@app.route('/api/getTempImage/<filename>')
def get_temp_image(filename):
    # image_directory = '/Users/programacao/dev/gpt/tempImages'
    image_directory = '/Users/programacao/dev/gpt/src/docx/imgsSmart'
    try:
        return send_from_directory(image_directory, filename, mimetype='image/png')  
    except FileNotFoundError:
        return "Image not found", 404
# @app.route('/api/getTempImage')
# def get_temp_image(filename):
#     image_directory = './mytempimageFileSaved/'
#     try:
#         return send_from_directory(image_directory, filename)
#     except FileNotFoundError:
#         return "Image not found", 404
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4014)
