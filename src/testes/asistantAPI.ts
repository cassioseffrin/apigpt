import OpenAI from "openai";
const openai = new OpenAI();
async function main() {
  let assistantId = "asst_flN0aLfDHU2Mg35WVKz0XIk1";
  console.log("Created Assistant with Id: " + assistantId);
  const thread = await openai.beta.threads.create({
    messages: [
      {
        role: "user",
        content: '"como acessar as visitas negativa e para que servem?"',
      },
    ],
  });
  const run = await openai.beta.threads.runs.createAndPoll(thread.id, {
    assistant_id: assistantId,
    additional_instructions: "é um cliente especial, caprichar na resposta",
  });
  if (run.status == "completed") {
    const messages = await openai.beta.threads.messages.list(thread.id);
    for (const message of messages.getPaginatedItems()) {
      console.log(message);
    }
  }
}
main();
