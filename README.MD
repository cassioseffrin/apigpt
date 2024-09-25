
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



python3 -m venv myenv
pip install --upgrade pip setuptools wheel
pip install python-docx pillow openai
pip install fuzzywuzzy python-Levenshtein
pip install sentence-transformers
pip install "numpy<2"    
pip3 install  load_dotenv
<!-- pip install transformers -->
<!-- pip install sentencepiece -->
<!-- pip install torch -->
<!-- pip install sentence_transformers -->
 
python3 src/extract_images_desc_below_Image.py "/home/arpa/apigpt/src/docx/smartv5.docx"  "/home/arpa/apigpt/src/docx/imgsSmart"  "asst_flN0aLfDHU2Mg35WVKz0XIk1"  "false" "false" 
python3 src/server.py




**Setor de documentacao tem obrigatoriamente deve conhecer muito o sistema para treinar o modelo.

**As bases de conhecimento foram melhoradas programaticamente.
    - Todas imagens foram extraídas. (A qualidade das imagens do docx estao muito baixas)
    - As imagens foram descritas por AI e acrescentadas no vector store com base nos textos. Referencias ao nomes aquivos imagens marcadas.
    - Titulos das imagens transferidas para a descricao das imagens, titulo removido pra evitar redundancias.
    - Apos GPT gerar resposta com base no texto mais descricoes das imagens ao achar referencia para arquivos foi criado agoritmo pra regatar as imagens com base na API.
    - Verificar questao apresentacao desta imagens (links, ou motrar tudo no chat)
    - 

**A API do GPT é generativa, mas as respostas para o assistente sao efemeras,  generativas para thread atual. Portanto;
    - Fazer testes com perguntas estratégicas com base em um check list.
    - Avaliar respostas e acrestentar no manual (vector store) as faltas de conhecimento (limbos) para evitar composicoes de resposta inconsistentes.
