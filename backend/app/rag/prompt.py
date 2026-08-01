from typing import List


class PromptBuilder:
    def build(self, question: str, context: List[str]) -> str:
        context_text = "\n\n".join(context) if context else "Aucun contexte disponible"
        
        prompt = f"""Tu es un assistant skills spécialisé dans les documents SDSI. 
Utilise le contexte suivant pour répondre à la question de manière précise et professionnelle.

Contexte:
{context_text}

Question: {question}

Réponse:"""
        
        return prompt
