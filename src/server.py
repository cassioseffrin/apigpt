from datetime import datetime
import json
import mimetypes
from flask import Flask, jsonify, request, send_from_directory 
import os
import openai
import sqlite3
import base64
from dotenv import load_dotenv
import re
from openai import OpenAI
import re
client = OpenAI()
# base_url_img = "https://assistant.arpasistemas.com.br/api/images/"
base_url_img = "https://assistant.arpasistemas.com.br/api/getImage/"
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
app = Flask(__name__)
import openai
from Levenshtein import distance as levenshtein_distance
import os
from flask import send_from_directory
import json



instructions = '''
PERSONAGEM: Você é o 'ASSISTENTE para Smart forca de vendas Um Chatbot com a capacidade de executar pesquisas avançadas baseadas em vector store para fornecer respostas contextualmente relevantes às consultas do usuário.
INSTRUÇÕES: Sempre redija a resposta para o USUÁRIO em português/Brasil, evitando respostas que não esteja presentes do vector store 
INSTRUÇÕES: Se o USUÁRIO perguntar sobre "tem alguma imagem" ou "tem um print da tela" ou "tem uma foto" ou "tem um exemplo de", retorne encontro no vector store atraves da string IMAGE_URI, limite-se a entregar imagens presentes paragrafo que contem relevancia a pergunta
INSTRUÇÕES: evite citação e referecia ao vector store (file_citation) ex:【4:1†source】não devem ser referenciados no texto para o User.
'''

def create_new_thread_and_talk(message):
 
    thread = openai.beta.threads.create(
        messages=[
            {
                'role': 'system',
                'content': instructions   
            },
            {
                'role': 'user',
                'content': message   
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
        assistant_id = "asst_9rmWBxwCmQay4hyaE7TST9tT"
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
    
def getAssistantId(assistant_name):
    data = [
        '"assistantName": "SMART",  "assistantID": asst_9rmWBxwCmQay4hyaE7TST9tT',
        '"assistantName": "VAREJO",  "assistantID": asst_92344Qay4534TST455352SXT',
        '"assistantName": "PDV",  "assistantID": asst_ERGDFB34s455352SgsgfdgXT'
    ]
    
    # Define the regex pattern
    pattern = re.compile(r'"assistantName": "{}".*?"assistantID": (asst_\w+)'.format(re.escape(assistant_name)))
    
    # Search through the data
    for entry in data:
        match = pattern.search(entry)
        if match:
            return match.group(1)  # Return the assistantID if found
    
    return None  # Return None if no match is found

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        # assistant_id = "asst_9rmWBxwCmQay4hyaE7TST9tT"
        thread_id = data['threadId']
        message = data['message']
        assistant_id = getAssistantId(data['assistantName'])
        # openai.beta.threads.messages.create(
        #     thread_id=thread_id,
        #     role='user',
        #     content=message
        # )
        response = continuar_conversar(thread_id, assistant_id, message)
        # if response:
        #     image_references = []
        #     for content_block in response.get('content', []):
        #         if 'source' in content_block:
        #             image_references.append(content_block)
        #     if image_references:
        #         url_images = {}
        #         for ref in image_references:
        #             description = ref
        #             images_urls = get_images_urls(message)
        #             url_images.update(images_urls)
        #         response['images'] = url_images
        return json.dumps(response), 200
    except Exception as error:
        print(f"Error: {error}")
        return "Internal Server Error", 500
@app.route('/webhookBitrix', methods=['POST'])
def webhook_bitrix():
    try:
        data = request.get_json()
        prompt = data['prompt']
        assistant_id = "asst_9rmWBxwCmQay4hyaE7TST9tT"
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
        return [message_to_json_response(msg) for msg in messages]
    else:
        return None
def conversar(thread_id, assistant_id):
    messages = process_messages(thread_id, assistant_id)
    if messages:
        for message in messages:
            print(message)
            return message_to_json_response(message)  
    else:
        return None
 
 


  
def extract_image_filenames(text):
    """Extract all image filenames from the text."""
    return re.findall(r'\b\w+_(?:figura|image|picture)[^\s]+\.(?:png|jpg|jpeg)\b', text)
 
 
def continuar_conversar(thread_id, assistant_id, message):
    openai.beta.threads.messages.create(
        thread_id=thread_id,
        role='user',
        content=message
    )
 
    run = openai.beta.threads.runs.create_and_poll(
        thread_id=thread_id,
        assistant_id=assistant_id,
        additional_instructions=instructions
    )
    if run.status == 'completed':
        messages = openai.beta.threads.messages.list(thread_id)
        if messages:
            last_message = messages.data[0]
            response_content = last_message.content[0]
            arrayImg = extract_image_filenames(response_content.text.value)
            for index, image_filename in enumerate(arrayImg):

 
                response_content.text.value = re.sub(
                    rf"{image_filename}",
                    f"",
                    response_content.text.value
                )

        
            # place in postition v1
            # for index, image_filename in enumerate(arrayImg):
            #     image_url = f"{base_url_img}{image_filename}"
            #     thumbnail = f'<a href="{image_url}" target="_blank"><img src="{image_url}" alt="Imagem {index+1}" width="30" height="30"></a>'
            #     response_content.text.value = response_content.text.value.replace(f"({image_filename})", thumbnail)
            # return message_to_json_response(last_message, arrayImg)
            #include on bottom
            # for index, image_filename in enumerate(arrayImg):
            #     image_url = f"{base_url_img}{image_filename}"
            #     thumbnail = f'<a href="{image_url}" target="_blank"><img src="{image_url}" alt="Imagem {index+1}" width="30" height="30"></a>'
            #     links.append(thumbnail)
            # all_thumbnails = "\n".join(links)
            # if len(all_thumbnails) > 0:
            #     last_message_content = f"{response_content.text.value} \n\n{all_thumbnails}"
            #     response_content.text.value = last_message_content
            #     return message_to_json_response(last_message, arrayImg)
            # arrayImg = extract_image_filenames(response_content.text.value)
            # for index, image_filename in enumerate(arrayImg):
            #     image_url = f"{base_url_img}{image_filename}"
            #     link_to_image = f'<a href="{image_url}">Imagem: {index+1}</a>'
            #     links.append(link_to_image)
            # all_links = "\n".join(links)
            # if len(all_links)>0:
            #     last_message_content = f"{last_message.content[0].text.value} \n\n{all_links}"
            #     last_message.content[0].text.value = last_message_content
            #     return message_to_json_response(last_message, arrayImg)
            # annotations =  response_content.text.annotations
            # citations = []
            # for index, annotation in enumerate(annotations):
            #     response_content.text.value = response_content.text.value.replace(annotation.text, f' [{index}]')
            #     if (file_citation := getattr(annotation, 'file_citation', None)):
            #         cited_file = client.files.retrieve(file_citation.file_id)
            #     elif (file_path := getattr(annotation, 'file_path', None)):
            #         cited_file = client.files.retrieve(file_path.file_id)
            return message_to_json_response(last_message, arrayImg)
        


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
        return [message_to_json_response(message) for message in messages]
    return None
def message_to_json_response_text_only(message):
    return {
        'id': message.id,
        'role': message.role,
        'content': [block.text.value for block in message.content],
        'created_at': message.created_at,
        'thread_id': message.thread_id
    }
def message_to_json_response(message, arrayImg):
    response = {
        'id': message.id,
        'role': message.role,
        'content': [block.text.value for block in message.content],
        'created_at': message.created_at,
        'thread_id': message.thread_id
    }
    if len(arrayImg) > 0:
        image_links = [
            f'{base_url_img}{image_filename}'
            # f'<a href="{base_url}{image_filename}">Clique aqui para ver a imagem correspondente</a>'
            for image_filename in arrayImg
        ]
        response['images'] = image_links
    return response
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
import os
from flask import send_from_directory, abort
@app.route('/api/getImage/<filename>')
def getImage(filename):    
    filepath = filename.split('_')[0]
    completefilename = filepath + "/" + filename
    image_directory = './imgs/'
    mimetype = mimetypes.guess_type(image_directory+completefilename)[0]
    try:
        return send_from_directory(image_directory, completefilename, mimetype=mimetype)
    except FileNotFoundError:
        return "Image not found", 404
@app.route('/api/getTempImage/<filepath>/<filename>')
def get_temp_image(filepath,filename):    
    completefilename =  filepath+"/"+filename
    try:
        return send_from_directory("./imgs/",completefilename , mimetype='image/png')  
    except FileNotFoundError:
        return "Image not found", 404
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4014)
