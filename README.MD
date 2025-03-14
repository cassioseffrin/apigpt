
pip freeze > requirements.txt



 para criar a lista de dependecias.

OLD
asst_flN0aLfDHU2Mg35WVKz0XIk1

Smart forca de vendas

Sou seu assistente do Smart forca de vendas. 

Pode perguntar qualquer coisa, estou preparado para ajudar!

NEW
asst_9rmWBxwCmQay4hyaE7TST9tT

https://github.com/openai/openai-node
https://assistant.arpasistemas.com.br/createNewThread
curl --request GET \
--url https://assistant.arpasistemas.com.br/createNewThread 
curl --request POST \
--url https://assistant.arpasistemas.com.br/chat \
--header 'Authorization: Bearer OPENAI_API_KEY' \
--header 'Content-Type: application/json' \
--data '{
    "threadId": "thread_VfDfc3rDziJJjmH77bXdNZBA",
    "assistant": "smart",
    "message": "o que ocorre quando uma tabela de precos for atualizada?"
}'


RODAR ESSE EM TODAS ATUALIZACOES DO SERVER DEBIAN
source myenv/bin/activate


Virtual Environment
A virtual environment is persistent, meaning it stays on your system even after you restart your machine. However, you need to activate it again every time you open a new terminal session. 
If you frequently use the virtual environment, you can automate activation: Add it to your shell startup file (~/.zshrc, ~/.bashrc, etc.):
echo "source /Users/arpasistemas/dev/gpt/myenv/bin/activate" >> ~/.zshrc
This will activate the environment automatically when opening a terminal.

Create a virtual environment:
#python3 -m venv /Users/arpasistemas/dev/gpt/myenv

Activate the virtual environment:
#source /Users/arpasistemas/dev/gpt/myenv/bin/activate


Install the packages inside the virtual environment:
 



EXECUTAR ISSO NO SERVIDOR PRA COLOCAR EM PRODUCAO
python3 -m venv /home/arpa/assistenteSmart/myenv
source /home/arpa/assistenteSmart/myenv/bin/activate
pip install python-docx pillow openai
pip install "numpy<2"    
pip install  load_dotenv
pip install  flask




/Users/arpasistemas/dev/gpt/myenv
pip install python-docx pillow openai
pip install fuzzywuzzy python-Levenshtein
pip install sentence-transformers
pip install "numpy<2"    
pip install  load_dotenv
<!-- pip3 install transformers -->
<!-- pip install sentencepiece -->
<!-- pip install torch -->
<!-- pip install sentence_transformers -->
 
python3 src/extract_images_desc_below_Image.py "/home/arpa/apigpt/src/docx/smartv5.docx"  "/home/arpa/apigpt/src/docx/imgsSmart"  "asst_flN0aLfDHU2Mg35WVKz0XIk1"  "false" "false" 
python3 src/server.py





python3 src/extract_images_desc_below_Image.py "/Users/arpasistemas/dev/gpt/src/docx/smartv7.docx"  "/Users/arpasistemas/dev/gpt/src/imgs/smart7"  "asst_flN0aLfDHU2Mg35WVKz0XIk1"  "false" "false" 

python3 src/server.py



REUNIAO PROXIMOS PASSOS IA
 
http://192.168.50.51/

**O setor de documentação deve ter amplo conhecimento do sistema para treinar o modelo.

**As bases de conhecimento foram melhoradas programaticamente:

- Todas as imagens foram extraídas. (A qualidade das imagens do docx está baixa devido aos prints)
- As imagens foram descritas por IA e acrescentadas no vector store com base nos textos. Referências aos nomes dos arquivos de imagens foram marcadas.
- Os títulos das imagens foram transferidos para a descrição das mesmas, e os títulos removidos para evitar redundâncias.
- Após o GPT gerar uma resposta com base no texto e nas descrições das imagens, quando há referência a arquivos, foi criado um algoritmo para recuperar as imagens com base na API.
- Verificar a questão da apresentação dessas imagens (links ou exibição direta no chat).

**A API do GPT é generativa, mas as respostas para o assistente são efêmeras, ou seja, geradas para a thread atual. Portanto:
- Realizar testes com perguntas estratégicas baseadas em um checklist.
- Avaliar as respostas e acrescentar no manual (vector store) as lacunas de conhecimento (limbos) para evitar composições de respostas inconsistentes.

*Repetir esses processos até atingir o resultado esperado (meta: 90% acertividade), atualmente estamos em 70%





 

    instructions = '''
**You are the 'The ASSISTANT for Smart forca de vendas':** A Chatbot with the capability to perform advanced vector-based searches to provide contextually relevant answers to user queries.
**Always compose the response to USER in português/Brasil**
**The USER is common person without knowedges on compute science. Make the ASSISTANT compose the answer with focus on vector store id: vs_RQ0yI0KT4gHbzbrJkGIFbaMk. 
**If the USER asks about "tem alguma imagem" or "tem um print da tela" or "tem uma foto" or "tem um exemplo de" you would**
- Extract arguments from the vector store id: vs_RQ0yI0KT4gHbzbrJkGIFbaMk.  avoid Image citation like this:  ![Imagem](smt_figura93.png)【4:1†source】, ASSISTANT must return just: smt_figura93.png instead.
- Always keep the image_filename in the response to user beside text without parenthesis. eg: (smt_figura93.png) become just smt_figura93.png
'''