import api from "./api";

export async function askQuestion(question) {
  const { data } = await api.post("/chat/", { question });
  return data;
}
