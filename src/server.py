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
from fuzzywuzzy import fuzz
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
def create_new_thread_and_talk(message):
    instructions = '''
**You are the 'The ASSISTANT for Smart forca de vendas':** A Chatbot with the capability to perform advanced vector-based searches to provide contextually relevant answers to user queries.
**Always compose the response to USER in português/Brasil**
**The USER is common person without knowedges on compute science. Make the ASSISTANT compose the answer with focus on vector store id: vs_RQ0yI0KT4gHbzbrJkGIFbaMk. 
**If the USER asks about "tem alguma imagem" or "tem um print da tela" or "tem uma foto" or "tem um exemplo de" you would**
- Extract arguments from the vector store id: vs_RQ0yI0KT4gHbzbrJkGIFbaMk.  avoid Image citation like this:  ![Imagem](smt_figura93.png)【4:1†source】, ASSISTANT must return just: smt_figura93.png instead.
- Always keep the image_filename in the response to user beside text without parenthesis, brackets quotes. eg: (smt_figura93.png) or [smt_figura93.png] or !(smt_figura93.png) must be returned as  just smt_figura93.png
'''
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
def get_delivery_date(filename: str) -> datetime:
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
            return message_to_json_response(last_message)  
    return None
import json
def gpt_similarity(text1, text2):
    response = openai.Completion.create(
        engine="gpt-4",
        prompt=f"Calculate similarity between '{text1}' and '{text2}' on a scale from 0 to 1.",
        max_tokens=10,
        temperature=0
    )
    similarity_score = float(response.choices[0].text.strip())
    return 1 - similarity_score  
def get_best_match_filename(user_input, db_path='images_assistant.db', relevance_threshold=0.60):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    query = "SELECT filename, title, description FROM images"
    cursor.execute(query)
    results = cursor.fetchall()
    connection.close()
    best_match_filename = None
    best_match_title = None
    best_match_score = 0
    loop = 0
    print(f"entrada: {user_input}")   
    for filename, title, description in results:
        match_score = max(
            gpt_similarity(user_input, title), 
            gpt_similarity(user_input, description)
        )
        print(f"{loop}: {match_score}: {title}")     
        loop += 1 
        if match_score > best_match_score:
            best_match_score = match_score
            best_match_filename = filename
            best_match_title = title
    print(f"Melhor score: {best_match_score}: {best_match_filename}: {best_match_title} ")            
    if best_match_score > relevance_threshold:
        return best_match_filename
    return None
vector_store_text = """
MANUAL SAMRT FORÇA DE VENDAS APP
INDICE
APRESENTAÇÃO
Este manual tem como finalidade demonstrar ao usuário o menu de pedidos do aplicativo Smart Vendas. Nele, será possível consultar pedidos já feitos, concluir pedidos que ainda estão pendentes de finalização, bem como, realizar um novo pedido.
Configuração do aplicativo - Este manual tem como principal objetivo detalhar as configurações do aplicativo no momento que o mesmo for baixado no aparelho para que o usuário inicie o uso.
Instalação dos módulos adicionais - Nesse manual, será explicado o processo para realizar a instalação dos serviços de módulos integrados ao Sistema Control. Vale lembrar que a instalação só deverá ser realizada se o Sistema Control já estiver em total funcionamento na máquina.
LIBERAÇÃO DO APLICATIVO NO CONTROL DESKTOP - O Smart Sales Force trata-se de uma aplicação adicional ao Sistema Control, que permite a realização de vendas online e offline através de um smartphone. Para utilizar o Smart Sales Force, inicialmente é necessário realizar algumas configurações no sistema Control conforme será demonstrado neste manual de instruções.
Manual de como efetuar o download do aplicativo em sistema Android
para versões acima de 2022 - Este manual tem como finalidade demonstrar ao usuário como realizar o download do aplicativo Smart Sales Force dentro da loja de seu
Smartphone com Sistema Android. Clientes que atualizarem o Sistema para a versão de 2022, terão os aplicativos atualizados pelas loja
de seu smartphone de forma automática (a depender das configurações do aparelho e política da loja).
Outro detalhe importante é que, em dado momento, o aplicativo irá atualizar automaticamente sozinho. Desta forma, assim que o
aplicativo se atualizar, o cliente deverá obrigatoriamente atualizar o Sistema Control Desktop.
Este manual tem como finalidade demonstrar ao usuário como realizar o download do aplicativo Smart Sales Force dentro da loja de seu Smartphone com sistema operacional IOS. Clientes que atualizarem o Sistema para a versão de 2022, terão os aplicativos atualizados pela loja de seu smartphone de forma automática (a depender das configurações do aparelho e política da loja).
Outro detalhe importante é que, em dado momento, o aplicativo irá atualizar automaticamente sozinho. Desta forma, assim que o aplicativo se atualizar, o cliente deverá obrigatoriamente atualizar o Sistema Control Desktop.
1. DOWNLOAD
1.1 DOWNLOAD DO APLICATIVO EM SISTEMA ANDROIND 
Para realizar o download do aplicativo Smat Sales Force o usuário deve localizar e acessar o aplicativo Play Store em seu aparelho, na próxima tele deve pressionar no menu pesquisar, conforme representado nas Figuras 01.
Figura 01: Tela inicial
A imagem mostra a interface da Google Play Store, na seção "Para você". No topo, estão destacados jogos como "Blood Strike", "Roblox" e "Tile Club". Abaixo, há uma lista de sugestões de jogos patrocinados, incluindo "Paciência", "Coin Master" e "Bubble Pop! Cannon Shooter", cada um acompanhado de informações de classificação e tamanho. Na parte inferior da tela, há ícones para navegar entre seções, incluindo "Jogos", "Apps", "Livros" e uma opção de "Pesquisar" destacada em vermelho. image_rId8.png
Fonte: Aplicativo Play Store, 2024.
O usuário deve digitar o nome do aplicativo Smat Sales Force e realizar a busca, na sequência deve pressionar sobre o ícone do aplicativo encontrado na pesquisa, conforme representado na Figura 02.
Figura 02: Menu Pesquisar
A imagem mostra uma tela de pesquisa na loja de aplicativos, onde o termo "smart sales force" está sendo utilizado. Os resultados incluem vários aplicativos, com destaque para "Smart Força de Vendas" da Arpa Sistemas, que possui uma classificação de 4,3 estrelas e 14 MB de tamanho, além de mais de mil downloads. Outros aplicativos listados incluem Salesforce, App Sales Force +, e Meta Sales Force, com diferentes classificações e tamanhos. A interface apresenta também um botão de instalação para os aplicativos. image_rId9.png
Fonte: Aplicativo Play Store, 2024.
Após efetuar o processo descrito acima, o operador será direcionado a outra tela, onde terá especificações referente ao aplicativo. Para baixá-lo, basta pressionar o botão Instalar e aguardar a finalização do download, conforme representado nas Figuras 03, 04 e 05.
Figura 03: Instalar
A imagem apresenta a interface do aplicativo "Smart Força de Vendas", desenvolvido pela Arpa Sistemas. Na parte superior, está o nome do aplicativo junto com a sua classificação de 4,2 estrelas, o número de avaliações (12) e o tamanho do aplicativo (14 MB). Abaixo, há uma chamada para ação para instalar o aplicativo. A imagem exibe também várias capturas de tela do aplicativo, mostrando suas funcionalidades. Há seções como "Sobre este app" e "Segurança dos dados" também apresentadas na parte inferior. Além disso, são visualizados ícones representando diferentes categorias como jogos, apps, e livros. image_rId10.png
Fonte: Aplicativo Play Store, 2024.
Figura 04: Instalando
A arguments
 "Smart Força de Vendas" em um dispositivo móvel. Acima, há um botão para cancelar ou abrir o aplicativo, além de um aviso indicando que ele é verificado pelo Play Protect. Abaixo, são apresentadas sugestões de aplicativos patrocinados, como "Nomad: Conta em Dólar e Cartão", "Livelo: juntar e trocar pontos" e "Estoque, Vendas, Pdv, Finanças", juntamente com mais opções de aplicativos para testar, incluindo "PictureThis Identificador Planta" e "CamScanner". A parte inferior da tela contém ícones de acesso a jogos, aplicativos, e livros. image_rId11.png
Fonte: Aplicativo Play Store, 2024.
"""
def extract_image_filenames(text):
    """Extract all image filenames from the text."""
    return re.findall(r'\b\w+_(?:figura|image)\d+\.(?:png|jpg|jpeg)\b', text)
def continuar_conversar_v7_nao_funciona(thread_id, assistant_id, message):
    openai.beta.threads.messages.create(
        thread_id=thread_id,
        role='user',
        content=message
    )
    instructions = '''
**You are the 'Vector store for Smart forca de vendas':** A Chatbot with the capability to perform advanced vector-based searches to provide contextually relevant answers to user queries.
**Responda sempre no idioma português Brasil**
**Instructions for Using the 'get_images' Tool:**
1. **Understanding the Tool:**
   - The "get_images" tool is designed to perform a contextually aware search based on vector store: smartv6_text.txt. It uses vector store content to extract the images inside vector store files.
2. **Identifying the User Query:**
   - Begin by identifying the user's query. Pay attention to the key concepts and specific details the user is interested in.
3. **Formulating the Search String:**
   - Based on the user's query, formulate a concise and targeted search string. Include the most important images based on the prompt context.
4. **Using the Tool:**
   - Pass the formulated search string to the "get_images" tool as an argument. The arguments must be a list of images present in the vector store, e.g., image_*.png or image_*.jpg must be included.
- Pass the string to the tool: `get_images(images_filenames)`
5. **Interpreting Results:**
   - Once the "get_images" returns results, analyze the information to verify its relevance and accuracy in addressing the user's query.
6. **Communicating the Outcome:**
   - Present the findings from the "get_images" to the user in a clear and informative manner, summarizing the context or providing a direct answer to the query.
**Example Usage:**
If the user asks about "tem alguma imagem", you would:
- Extract arguments from the vector store: smartv6_text.txt. All strings that have image_*.png or image_*.jpg must be included.
- Pass the string to the tool: `get_images(arguments)`
- Analyze and relay the information back to the user in response to their query.
Remember to maintain the user's original intent in the search string and to ensure that the results from the "vector_get_image" are well-interpreted before conveying them to the user.
'''
    run = openai.beta.threads.runs.create_and_poll(
        thread_id=thread_id,
        assistant_id=assistant_id,
        additional_instructions=instructions,
        tools=[{
            "type": "function",
            "function": {
                "name": "get_images",
                "description": "Perform a get_images search to retrieve image links based on input user prompt.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "array", "items": {"type": "string"}, "description": "A list of image filenames extracted from the vector store context."},
                    },
                    "required": ["query"]
                }
            },
        }]
    )
    if run.status == "requires_action":
        if run.required_action.submit_tool_outputs.tool_calls[0].type == 'function':
            tool_function = run.required_action.submit_tool_outputs.tool_calls[0].function
            function_name = getattr(tool_function, 'name')
            arguments = getattr(tool_function, 'arguments')
            result = getImage(arguments['query'])
            run = openai.beta.threads.runs.submit_tool_outputs(
                thread_id=thread_id,
                run_id=run.id,
                tool_outputs=[
                    {
                        "tool_call_id": run.required_action.submit_tool_outputs.tool_calls[0].id,
                        "output": json.dumps(result),
                    },
                ]
            )
    if run.status == 'completed':
        messages = openai.beta.threads.messages.list(thread_id)
        if messages:
            last_message = messages.data[0]
            response_content = last_message.content[0]
            return message_to_json_response(response_content)
    return None
def continuar_conversar_v6_incompleto(thread_id, assistant_id, message):
    openai.beta.threads.messages.create(
        thread_id=thread_id,
        role='user',
        content=message
    )
    instructions = '''
**You are the 'Vector store for Smart forca de vendas':** A Chatbot with the capability to perform advanced vector-based searches to provide contextually relevant answers to user queries.
**Responda sempre no idioma português Brasil**
**Instructions for Using the 'get_images' Tool:**
1. **Understanding the Tool:**
   - The "get_images" tool is designed to perform a contextually aware search based on vector store: smartv6_text.txt. It uses vector store content to extract the images inside vector store files.
2. **Identifying the User Query:**
   - Begin by identifying the user's query. Pay attention to the key concepts and specific details the user is interested in.
3. **Formulating the Search String:**
   - Based on the user's query, formulate a concise and targeted search string. Include the most important images based on the propmt context.
4. **Using the Tool:**
   - Pass the formulated search string to the "get_images" tool as an argument. the arguments must be a list of images present on the vector store, eg: image_*.png or image_*.jpg must be included
- Pass the string to the tool: `get_images(images_filenames)`
5. **Interpreting Results:**
   - Once the "get_images" returns results, analyze the information to verify its relevance and accuracy in addressing the user's query.
6. **Communicating the Outcome:**
   - Present the findings from the "get_images" to the user in a clear and informative manner, summarizing the context or providing a direct answer to the query.
**Example Usage:**
If the user asks about "tem alguma imagem" you would:
- Extract arguments from the vector store: smartv6_text.txt. All strings that have image_*.png or image_*.jpg must be included
- Pass the string to the tool: `get_images(arguments)`
- Analyze and relay the information back to the user in response to their query.
Remember to maintain the user's original intent in the search string and to ensure that the results from the "vector_get_image" are well-interpreted before conveying them to the user.
'''
    # Run the assistant's response generation with additional instructions
    run = openai.beta.threads.runs.create_and_poll(
        thread_id=thread_id,
        assistant_id=assistant_id,
        additional_instructions=instructions,
        tools=[{
            "type": "function",
            "function": {
                "name": "get_images",
                "description": "Perform a get_images search to retrieve images links based on input user prompt.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "A targeted search string based on a user query."},
                    },
                    "required": ["query"]
                }
            },
        }]
        )
    if run.status == "requires_action":
        if run.required_action.submit_tool_outputs.tool_calls[0].type == 'function':
            # Get the name of the tool and arguments to pass to it, from GPT4's understanding from our instructions
            tool_function = run.required_action.submit_tool_outputs.tool_calls[0].function
            function_name = getattr(tool_function, 'name')
            arguments = getattr(tool_function, 'arguments')
            # Now call the function from the tools dictionary using the function name
            result = getImage(arguments)
            # Pass the tool's output result for more processing
            run = client.beta.threads.runs.submit_tool_outputs(
                thread_id=thread_id,
                run_id=run.id,
                tool_outputs=[
                    {
                        "tool_call_id": run.required_action.submit_tool_outputs.tool_calls[0].id,
                        "output": json.dumps(result),
                    },
                ]
            )
    if run.status == 'completed':
        messages = openai.beta.threads.messages.list(thread_id)
        if messages:
            last_message = messages.data[0]
            response_content = last_message.content[0]
            return message_to_json_response(response_content)
    return None
def continuar_conversar(thread_id, assistant_id, message):
    openai.beta.threads.messages.create(
        thread_id=thread_id,
        role='user',
        content=message
    )
#     instructions = '''
# **PERSONAGEM: Você é o 'Assistente virtual do Smart forca de vendas': Um Chatbot com a capacidade de realizar pesquisas avançadas baseadas em vetores para fornecer respostas contextualmente relevantes às consultas dos usuários.
# **INSTRUÇÕES: 
#  - Responda sempre no idioma português Brasil
# ** Se o usuário perguntar sobre "tem alguma imagem", "tem um print da tela" ou "tem uma foto da tela" você deve:
#  - Sempre manter o image_filename na resposta ao usuário junto à anotação das citações, por exemplo: (smtv6_image_rId100.png ou gerv1_image_rId008.jpg ou gerv1_image_rId89.jpeg). Ou seja, todas as sequências image.png, image.jpg ou image.jpg, onde o * (asterisco) pode ser qualquer string.
#  - Os nomes dos aquivos de imagens (png, jpg ou jpeg) serão precedidos pela string IMAGE_FILENAME. Ex:  IMAGE_FILENAME: (smtv6_image_rId100.png)
#  - Ao encontrar referencias as imagens sempre confrontar com o vector store: sourceImages.json. A imagem deve estar com nomes coesos e integros presentes neste aquivo sourceImages.json
# EXEMPLOS: Procure fornecer as respostas com maximo de integridade e focadas nos manuais presentes no vector store.
# '''
    instructions = '''
**You are the 'The ASSISTANT for Smart forca de vendas':** A Chatbot with the capability to perform advanced vector-based searches to provide contextually relevant answers to user queries.
**Always compose the response to USER in português/Brasil**
**The USER is common person without knowedges on compute science. Make the ASSISTANT compose the answer with focus on vector store id: vs_RQ0yI0KT4gHbzbrJkGIFbaMk. 
**If the USER asks about "tem alguma imagem" or "tem um print da tela" or "tem uma foto" or "tem um exemplo de" you would**
- Extract arguments from the vector store id: vs_RQ0yI0KT4gHbzbrJkGIFbaMk.  avoid Image citation like this:  ![Imagem](smt_figura93.png)【4:1†source】, ASSISTANT must return just: smt_figura93.png instead.
- Always keep the image_filename in the response to user beside text without parenthesis, brackets quotes. eg: (smt_figura93.png) or [smt_figura93.png] or !(smt_figura93.png) must be returned as  just smt_figura93.png
'''
# - Always keep the image_filename in the response to user beside the citations annotation. eg: (ger_figura52.png or smt_figura8.png). Ex:  ![Imagem](smt_figura93.png)【4:1†source】, neste caso retorne apenas (smt_figura93.png)
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
            links = []
            arrayImg = extract_image_filenames(response_content.text.value)
            for index, image_filename in enumerate(arrayImg):
                image_url = f"{base_url_img}{image_filename}"
                thumbnail = f'<a href="{image_url}" target="_blank"><img src="{image_url}" alt="Imagem {index+1}" width="70" height="70" style="border:1px solid grey; padding:0; margin:0;"></a>'
                response_content.text.value = re.sub(
                    rf"\({image_filename}\)",
                    image_filename,
                    response_content.text.value
                )
                response_content.text.value = re.sub(
                    rf"{image_filename}",
                    f":\n{thumbnail}",
                    response_content.text.value
                )

                response_content.text.value  = re.sub(
                    r"\>\.",
                    ">",
                    response_content.text.value
                )



                # response_content.text.value = re.sub(
                #     rf"{image_filename}",
                #     f".\n{thumbnail}",
                #     response_content.text.value
                # )

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
        

# 'Sim, há prints das telas relacionadas ao cadastro de um cliente. Você pode visualizar as imagens a seguir:\n\n- Figura 06: .\n<a href="https://assistant.arpasistemas.com.br/api/getImage/ger_figura06.png" target="_blank"><img src="https://assistant.arpasistemas.com.br/api/getImage/ger_figura06.png" alt="Imagem 1" width="70" height="70" style="border:1px solid grey; padding:0; margin:0;"></a>\n- Figura 07: .\n<a href="https://assistant.arpasistemas.com.br/api/getImage/ger_figura07.png" target="_blank"><img src="https://assistant.arpasistemas.com.br/api/getImage/ger_figura07.png" alt="Imagem 2" width="70" height="70" style="border:1px solid grey; padding:0; margin:0;"></a>\n- Figura 85: .\n<a href="https://assistant.arpasistemas.com.br/api/getImage/smt_figura85.png" target="_blank"><img src="https://assistant.arpasistemas.com.br/api/getImage/smt_figura85.png" alt="Imagem 3" width="70" height="70" style="border:1px solid grey; padding:0; margin:0;"></a>\n- Figura 86: .\n<a href="https://assistant.arpasistemas.com.br/api/getImage/smt_figura86.png" target="_blank"><img src="https://assistant.arpasistemas.com.br/api/getImage/smt_figura86.png" alt="Imagem 4" width="70" height="70" style="border:1px solid grey; padding:0; margin:0;"></a>\n- Figura 87: .\n<a href="https://assistant.arpasistemas.com.br/api/getImage/smt_figura87.png" target="_blank"><img src="https://assistant.arpasistemas.com.br/api/getImage/smt_figura87.png" alt="Imagem 5" width="70" height="70" style="border:1px solid grey; padding:0; margin:0;"></a>\n- Figura 88: .\n<a href="https://assistant.arpasistemas.com.br/api/getImage/smt_figura88.png" target="_blank"><img src="https://assistant.arpasistemas.com.br/api/getImage/smt_figura88.png" alt="Imagem 6" width="70" height="70" style="border:1px solid grey; padding:0; margin:0;"></a>\n- Figura 89: .\n<a href="https://assistant.arpasistemas.com.br/api/getImage/smt_figura89.png" target="_blank"><img src="https://assistant.arpasistemas.com.br/api/getImage/smt_figura89.png" alt="Imagem 7" width="70" height="70" style="border:1px solid grey; padding:0; margin:0;"></a>\n\nEssas imagens fornecem uma representação visual das telas e campos mencionados no processo de cadastro de um cliente.'
 

    return None
def continuar_conversar_v4(thread_id, assistant_id, message):
    best_filename = get_best_match_filename(message)
    if best_filename:
        image_url = f"https://assistant.arpasistemas.com.br/api/images/{best_filename}"
        assistant_message = f"Encontrei este print no manual: [Clique aqui para ver]({image_url})"
    else:
        assistant_message = None
    openai.beta.threads.messages.create(
        thread_id=thread_id,
        role='user',
        content=message
    )
    run = openai.beta.threads.runs.create_and_poll(
        thread_id=thread_id,
        assistant_id=assistant_id,
        additional_instructions='Responda no idioma português Brasil'
    )
    if run.status == 'completed':
        messages = openai.beta.threads.messages.list(thread_id)
        if messages:
            last_message = messages.data[0]
            if assistant_message:
                last_message_content = f"{last_message.content[0].text.value} \n\n{assistant_message}"
                last_message.content[0].text.value = last_message_content
            return message_to_json_response(last_message)
    return None
def continuar_conversar_v3(thread_id, assistant_id, message):
    best_filename = get_best_match_filename(message)
    if best_filename:
        image_url = f"https://assistant.arpasistemas.com.br/api/images/{best_filename}"
        assistant_message = f"Encontrei este print no manual: [Clique aqui para ver]({image_url})"
    else:
        assistant_message = None
    messages = [
        {"role": "system", "content": "Você é um assistente de suporte ao cliente prestativo. Responda no idioma português Brasil. Se você não encontrar a resposta no manual, não tente inventar uma resposta aleatória."},
        {"role": "user", "content": message}
    ]
    if assistant_message:
        messages.append({"role": "assistant", "content": assistant_message})
    client.chat.completions.create(
        model='gpt-4',
        messages=messages 
    )
    run = openai.beta.threads.runs.create_and_poll(
        thread_id=thread_id,
        assistant_id=assistant_id,
          additional_instructions='Responda no idioma português Brasil'
    )
    if run.status == 'completed':
        messages = openai.beta.threads.messages.list(thread_id)
        if messages:
            last_message = messages.data[0]
            if assistant_message:
                last_message_content = f"{last_message.content[0].text.value} \n\n{assistant_message}"
                last_message.content[0].text.value = last_message_content
            return message_to_json_response(last_message)
    return None
def continuar_conversar_v2(thread_id, assistant_id, message):
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_image",
                "description": "get the image of documentation on assistant vector store images.json. Call this whenever the user have somehow mention the image based on description on the vector store images.json.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "the image filename"
                        }
                    },
                    "required": ["filename"],
                    "additionalProperties": False
                }
            }
        }
    ]
    messages = []
    # messages.append({"role": "system", "content": "You are a helpful customer support assistant. please look into Vector store for Smart forca de vendas if the user prompt has any relation with title or description of Vector store images.json, and then please return the property filename of the vector store images.json and then supplied on tools to assist the user."})
    messages.append({"role": "system", "content": "You are a helpful customer support assistant. Please look into Vector store for Smart Força de Vendas images. If the user prompt has any relation with the title or description in the Vector store images.json, return the exact filename provided in images.json."})
    messages.append({"role": "user", "content": message})
    response = client.chat.completions.create(
        model='gpt-4o',
        messages=messages,
        tools=tools
    )
    tool_call = response.choices[0].message.tool_calls 
    if tool_call:
        arguments = json.loads(tool_call[0].function.arguments)
        filename = arguments.get('filename')
        if filename:
            delivery_date = get_delivery_date(filename)
            data = delivery_date.strftime('%Y-%m-%d %H:%M:%S')
            print(delivery_date)
            function_call_result_message = {
                "role": "tool",
                "content": json.dumps({
                    "filename": filename,
                    "delivery_date": data
                }),
                "tool_call_id": tool_call[0].id
            }
            print(function_call_result_message)
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
            return message_to_json_response(last_message)  
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
