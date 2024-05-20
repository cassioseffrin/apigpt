const express = require('express');
const fs = require('fs');
const { Configuration, OpenAI } = require("openai");
const app = express();
const PORT = process.env.PORT || 8080;
const requiredVersion = '1.1.1';
const currentVersion = require('openai/package.json').version;
const OPENAI_API_KEY = process.env.OPENAI_API_KEY;
if (currentVersion < requiredVersion) {
  throw new Error(`Error: versao ${currentVersion} menor que a requerida  ${requiredVersion}`);
} else {
  console.log('OpenAI compativel.');
}
const openai = new OpenAI(OPENAI_API_KEY);
function createAssistant() {
  const assistantFilePath = 'assistant.json';
  if (fs.existsSync(assistantFilePath)) {
    const assistantData = fs.readFileSync(assistantFilePath, 'utf8');
    const { assistant_id } = JSON.parse(assistantData);
    return assistant_id;
  } else {
    const file = openai.files.create({
      file: fs.createReadStream('baseconhecimento.docx'),
      purpose: 'assistants'
    });
    const assistant = openai.assistants.create({
      instructions: `
       Introducao ao smart forca de vendas
      `,
      model: 'gpt-4-1106-preview',
      tools: [{ type: 'retrieval' }],
      file_ids: [file.id]
    });
    const assistantId = assistant.id;
    fs.writeFileSync(assistantFilePath, JSON.stringify({ assistant_id: assistantId }));
    return assistantId;
  }
}
app.get('/start', (req, res) => {
  openai.threads.create().then(thread => {
    console.log(`nava thread ID: ${thread.id}`);
    res.json({ thread_id: thread.id });
  }).catch(err => {
    res.status(500).json({ error: 'Internal server error' });
  });
});
app.post('/chat', express.json(), (req, res) => {
  const { thread_id, message } = req.body;
  if (!thread_id) {
    return res.status(400).json({ error: 'falta o thread id' });
  }
  openai.threads.messages.create({
    thread_id,
    role: 'user',
    content: message
  }).then(() => {
    return openai.threads.runs.create({
      thread_id,
      assistant_id: assistantId
    });
  }).then(run => {
    const checkRunStatus = () => {
      openai.threads.runs.retrieve({ thread_id, run_id: run.id }).then(runStatus => {
        console.log(`Run status: ${runStatus.status}`);
        if (runStatus.status === 'completed') {
          openai.threads.messages.list({ thread_id }).then(messages => {
            const response = messages.data[0].content[0].text.value;
            res.json({ response });
          }).catch(err => {
            res.status(500).json({ error: 'Internal server error' });
          });
        } else {
          setTimeout(checkRunStatus, 1000);
        }
      }).catch(err => {
        res.status(500).json({ error: 'Internal server error' });
      });
    };
    checkRunStatus();
  }).catch(err => {
    res.status(500).json({ error: 'Internal server error' });
  });
});
const assistantId = createAssistant();
app.listen(PORT, () => {
  console.log(`servidor rodando porta: ${PORT}`);
});
