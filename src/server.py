from flask import Flask, request, jsonify
import os
import openai
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

app = Flask(__name__)
openai.api_key = OPENAI_API_KEY

# Function to create a new thread and send a message
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

# Endpoint to start a new thread and talk
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

# Function to create a new thread
def create_new_thread():
    return openai.beta.threads.create()

# Endpoint to create a new thread
@app.route('/createNewThread', methods=['GET'])
def create_new_thread_endpoint():
    try:
        thread = create_new_thread()
        return jsonify({'threadId': thread.id if thread else None}), 200
    except Exception as e:
        print(f"Error: {e}")
        return "Error creating thread", 500

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
            thread_id=thread_id,  # Keyword argument for thread_id
            role='user',
            content=message
        )
        
        # Process and respond
        response = continuar_conversar(thread_id, assistant_id, message)
        return jsonify(response), 200
    except Exception as error:
        print(f"Error: {error}")
        return "Internal Server Error", 500

# Webhook for Bitrix
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

# Conversar function for a new Bitrix thread
def conversar_nova_thread_bitrix(thread_id, assistant_id, message):
    openai.beta.threads.messages.create(
        thread_id=thread_id,  # Keyword argument for thread_id
        role='user',
        content=message
    )
    run = openai.beta.threads.runs.create_and_poll(
        thread_id=thread_id,  # Keyword argument for thread_id
        assistant_id=assistant_id
    )
    if run.status == 'completed':
        messages = openai.beta.threads.messages.list(thread_id)
        return [message_to_dict(msg) for msg in messages]
    else:
        return None

# Conversar function
def conversar(thread_id, assistant_id):
    messages = process_messages(thread_id, assistant_id)
    if messages:
        for message in messages:
            print(message)
            return message_to_dict(message)  # Convert message to dict
    else:
        return None

# Continuar Conversar function

# Continuar Conversar function
def continuar_conversar(thread_id, assistant_id, message):
    openai.beta.threads.messages.create(
        thread_id=thread_id,  # Keyword argument for thread_id
        role='user',
        content=message
    )

    run = openai.beta.threads.runs.create_and_poll(
        thread_id=thread_id,  # Keyword argument for thread_id
        assistant_id=assistant_id
    )

    if run.status == 'completed':
        messages = openai.beta.threads.messages.list(thread_id)
        if messages:
            last_message = messages.data[0]  # Get the last message
            print(last_message)
            return message_to_dict(last_message)  # Convert message to dict
    return None

# Process messages
def process_messages(thread_id, assistant_id):
    run = openai.beta.threads.runs.create_and_poll(
        thread_id=thread_id,  # Keyword argument for thread_id
        assistant_id=assistant_id,
        additional_instructions=''
    )
    print(f"Processamento finalizado: {run.status}")
    if run.status == 'completed':
        messages = openai.beta.threads.messages.list(thread_id)
        return [message_to_dict(message) for message in messages]
    return None

# Helper function to convert a Message object to a serializable dictionary
def message_to_dict(message):
    return {
        'id': message.id,
        'role': message.role,
        'content': [block.text.value for block in message.content],
        'created_at': message.created_at,
        'thread_id': message.thread_id
    }

# Start the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4014)
