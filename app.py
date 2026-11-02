
import os

import streamlit as st
from dotenv import load_dotenv
from google import genai

load_dotenv()

st.set_page_config(
    page_title="FinancIA",
    page_icon="💰",
    layout="centered"
)

# Configuração Gemini
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("Chave da API não encontrada no arquivo .env")
    st.stop()

client = genai.Client(api_key=api_key)

MODELO = "gemini-3.5-flash-lite"

# Personalidade do agente
INSTRUCOES = """
Você é o FinancIA, um assistente de IA
especializado em educação financeira.

Suas responsabilidades:
- Explicar conceitos financeiros de forma clara.
- Ajudar a entender orçamento e planejamento.
- Explicar investimentos e juros compostos.
- Apresentar exemplos práticos quando necessário.
- Responder sempre em português brasileiro.
- Manter uma linguagem amigável e objetiva.
- Não prometer retornos financeiros.
- Não recomendar investimentos específicos como
  garantidos ou livres de risco.
"""

# Inicializa o histórico da conversa
if "mensagens" not in st.session_state:
    st.session_state.mensagens = []

# Cabeçalho
st.title("FinancIA")
st.caption("Seu assistente inteligente de educação financeira")

st.divider()

# Botão para limpar a conversa
if st.button("🗑️ Limpar"):
    st.session_state.mensagens = []
    st.rerun()

# Exibe as mensagens anteriores
for mensagem in st.session_state.mensagens:
    with st.chat_message(mensagem["role"]):
        st.markdown(mensagem["content"])

# Campo de entrada do usuário
pergunta = st.chat_input("Pergunte algo sobre finanças...")

if pergunta:

    # Adiciona a pergunta ao histórico
    st.session_state.mensagens.append({
        "role": "user",
        "content": pergunta
    })

    with st.chat_message("user"):
        st.markdown(pergunta)

    # Gera resposta da IA
    with st.chat_message("assistant"):
        with st.spinner("FinancIA está pensando..."):
            
            try:
                # Converte o histórico para o formato correto
                historico_gemini = []

                for mensagem in st.session_state.mensagens:
                    role = (
                        "model"
                        if mensagem["role"] == "assistant"
                        else "user"
                    )

                    historico_gemini.append({
                        "role": role,
                        "parts": [
                            {"text": mensagem["content"]}
                        ]
                    })

                # Envia o histórico completo para o Gemini
                resposta = client.models.generate_content(
                    model=MODELO,
                    contents=historico_gemini,
                    config={
                        "system_instruction": INSTRUCOES
                    }
                )

                texto = resposta.text

                if not texto:
                    raise ValueError("O modelo não retornou texto.")

                st.markdown(texto)

                # Salva a resposta no histórico do Streamlit
                st.session_state.mensagens.append({
                    "role": "assistant",
                    "content": texto
                })

            except Exception as erro:
                st.error(f"Erro ao consultar a IA: {erro}")