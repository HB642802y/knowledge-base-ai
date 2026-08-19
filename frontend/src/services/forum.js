import api from "./api";

export async function listQuestions() {
  const { data } = await api.get("/forum/questions");
  return data;
}

export async function getQuestion(id) {
  const { data } = await api.get(`/forum/questions/${id}`);
  return data;
}

export async function createQuestion({ title, body, author }) {
  const { data } = await api.post("/forum/questions", {
    title,
    body,
    author: {
      id: author.id,
      full_name: author.full_name,
      email: author.email,
    },
  });
  return data;
}

export async function createAnswer(questionId, { body, author }) {
  const { data } = await api.post(`/forum/questions/${questionId}/answers`, {
    body,
    author: {
      id: author.id,
      full_name: author.full_name,
      email: author.email,
    },
  });
  return data;
}

export async function deleteQuestion(questionId) {
  await api.delete(`/forum/questions/${questionId}`);
}

export async function deleteAnswer(answerId) {
  await api.delete(`/forum/answers/${answerId}`);
}
