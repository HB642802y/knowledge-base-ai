import api from "./api";

export async function getCollaboratorStats() {
  const { data } = await api.get("/stats/collaborator");
  return data;
}
