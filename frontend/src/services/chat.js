import api from "./api";

export async function askQuestion(question) {
  const { data } = await api.post("/chat/", { question });
  return data;
}

export async function listChatQuestions(options = {}) {
  const config = options.public ? { headers: { "X-User-Email": "" } } : undefined;
  const { data } = await api.get("/chat/questions", config);
  return data;
}

export async function createChatQuestion(question) {
  const { data } = await api.post("/chat/questions", { question });
  return data;
}

export async function addChatComment(questionId, body) {
  const { data } = await api.post(`/chat/questions/${questionId}/comments`, { body });
  return data;
}

export async function deleteChatQuestion(questionId) {
  await api.delete(`/chat/questions/${questionId}`);
}
