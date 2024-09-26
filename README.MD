
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





A gestão de pedidos no aplicativo é ilustrada através de várias telas que mostram diferentes estágios do processo de pedido. Aqui estão algumas imagens e descrições das telas relevantes:

Mudar para Concluir:

Esta tela mostra a opção de mudar o status de um pedido de "Em Andamento" para "Concluído". Há um botão verde destacado para essa ação (smt_figura66.png).
Status Concluído:

Após mudar o status, a tela exibe os pedidos com o status "Concluído", mostrando detalhes como o total e a hora da criação (smt_figura67.png).
Menu Pedido:

A tela do menu de pedidos lista os pedidos com opções para alterar o status diretamente da lista, facilitando a gestão rápida dos pedidos (smt_figura68.png).
Confirmação de Mudança de Status:

Quando uma mudança de status é iniciada, o aplicativo apresenta uma mensagem de confirmação para que o usuário escolha entre "Sim" ou "Não" para proceder com a mudança (smt_figura69.png).
Estas telas ajudam a visualizar e gerenciar o status dos pedidos de forma eficiente no aplicativo .

