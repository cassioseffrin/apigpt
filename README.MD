
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



source myenv/bin/activate
python3 -m venv myenv
pip install --upgrade pip setuptools wheel
pip install python-docx pillow openai
pip install fuzzywuzzy python-Levenshtein
pip install sentence-transformers
pip install "numpy<2"    

<!-- pip install transformers -->
<!-- pip install sentencepiece -->
<!-- pip install torch -->
<!-- pip install sentence_transformers -->
 
python3 src/extract_images_desc_below_Image.py "/home/arpa/apigpt/src/docx/smartv5.docx"  "/home/arpa/apigpt/src/docx/imgsSmart"  "asst_flN0aLfDHU2Mg35WVKz0XIk1"  "false" "false" 
python3 src/server.py