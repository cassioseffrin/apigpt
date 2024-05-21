import OpenAI from "openai";
import express, { Request, Response } from "express";
require('dotenv').config();
const OPENAI_API_KEY =  process.env.OPENAI_API_KEY;
const app = express();
app.use(express.json());
const openai = new OpenAI({apiKey:OPENAI_API_KEY});
async function createNewThreadAndTalk(message: string): Promise<any> {
  const thread = await openai.beta.threads.create({
    messages: [
      {
        role: "user",
        content: message,
      },
    ],
  });
  return thread;
}

app.post("/startThreadAndTalk", async (req: Request, res: Response) => {
  try {
    const { message } = req.body;
    const thread = await createNewThreadAndTalk(message);
    let assistantId = "asst_flN0aLfDHU2Mg35WVKz0XIk1";
    let response = (await conversar(thread.id, assistantId)) as any;
    response = { threadId: thread.id, ...response };
    res.status(200).send(JSON.stringify(response));
  } catch (e) {
    console.error(e);
    res.status(500).send("erro");
  }
});

async function createNewThread(): Promise<any> {
  const thread = await openai.beta.threads.create();
  return thread;
}

// app.listen("4014", () => {
//   console.log("Assistente iniciado!");
// });

app.listen(4014, '0.0.0.0', () => {
  console.log('Assistente iniciado!');
});

app.get("/createNewThread", async (req: Request, res: Response) => {
  try {
    const thread = await createNewThread();
    res.status(200).send({ threadId: thread?.id ?? null });
  } catch (e) {
    console.error(e);
    res.status(500).send("erro ao iniciar thread");
  }
});

app.post("/chat", async (req: Request, res: Response) => {
  try {
    let assistantId = "asst_flN0aLfDHU2Mg35WVKz0XIk1";
    const { threadId, message } = req.body;
    console.log("Thread ID:", threadId);
    console.log("Message:", message);
    const response = await continuarConversar(threadId, assistantId, message);
    res.status(200).send(JSON.stringify(response));
  } catch (error) {
    console.error("Error:", error);
    res.status(500).send("Internal Server Error");
  }
});

app.post("/webhookBitrix", async (req: Request, res: Response) => {
  try {
    let assistantId = "asst_flN0aLfDHU2Mg35WVKz0XIk1";
    const thread = await createNewThread();
    const {   prompt } = req.body;
    console.log("nova thread: ", thread.id);
    console.log("Mensagem a ser processada:", prompt);
    const response = await conversarNovaThreadBitrix(thread.id, assistantId, prompt);
    res.status(200).send(JSON.stringify(response));
  } catch (error) {
    console.error("Error:", error);
    res.status(500).send("Internal Server Error");
  }
});


async function conversarNovaThreadBitrix(
  threadId: any,
  assistantId: string,
  message: string
) {
  await openai.beta.threads.messages.create(threadId, {
    role: "user",
    content: message,
  });

  const run = await openai.beta.threads.runs.createAndPoll(threadId, {
    assistant_id: assistantId,
    // additional_instructions: message,
  });

  if (run.status == "completed") {
    const messages = await openai.beta.threads.messages.list(threadId);

    return messages.getPaginatedItems();
    // for (const message of messages.getPaginatedItems()) {
    //   // console.log(message);
    //   return message?.content ?? [];
    //   break;
    // }
  } else {
    return null;
  }
}


async function conversar(threadId: any, assistantId: string) {
  const messages = await processMessages(threadId, assistantId);
  if (messages != null) {
    for (const message of messages.getPaginatedItems()) {
      console.log(message);
      return message?.content[0] ?? {};
      break;
    }
  } else {
    return null;
  }
}

async function continuarConversar(
  threadId: any,
  assistantId: string,
  message: string
) {
  await openai.beta.threads.messages.create(threadId, {
    role: "user",
    content: message,
  });

  const run = await openai.beta.threads.runs.createAndPoll(threadId, {
    assistant_id: assistantId,
    // additional_instructions: message,
  });

  if (run.status == "completed") {
    const messages = await openai.beta.threads.messages.list(threadId);
    for (const message of messages.getPaginatedItems()) {
      console.log(message);
      return message?.content[0] ?? {};
      break;
    }
  } else {
    return null;
  }
}

async function processMessages(
  threadId: string,
  assistantId: string
): Promise<any> {
  const run = await openai.beta.threads.runs.createAndPoll(threadId, {
    assistant_id: assistantId,
    additional_instructions: "",
  });
  console.log("processamento finalizado: " + run.status);
  if (run.status == "completed") {
    const messages = await openai.beta.threads.messages.list(threadId);
    for (const message of messages.getPaginatedItems()) {
      console.log(message);
      break;
    }
    return messages;
  }
  return null;
}
