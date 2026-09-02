import api from "./api";

export async function listDocuments() {
  const { data } = await api.get("/documents/");
  return data;
}

export async function deleteDocument(documentId) {
  await api.delete(`/documents/${documentId}`);
}
