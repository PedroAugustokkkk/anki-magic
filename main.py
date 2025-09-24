# Importa as bibliotecas necessárias
import streamlit as st               # Para criar a interface web
import google.generativeai as genai  # Para usar a API do Gemini
import pandas as pd                  # Para criar e manipular o dataframe para o CSV
from io import StringIO              # Para permitir que o pandas leia uma string como se fosse um arquivo
import os                            # Para acessar variáveis de ambiente (nossa chave API)
from dotenv import load_dotenv       # Para carregar as variáveis do arquivo .env

# --- Carregando a Chave da API ---
# A função load_dotenv() lê o arquivo .env e carrega suas variáveis no ambiente
load_dotenv()

# Lógica inteligente para pegar a chave da API:
# 1. Tenta pegar do Streamlit Secrets (quando estiver online/deployado)
# 2. Se não encontrar, tenta pegar das variáveis de ambiente (carregadas do .env para rodar local)
try:
    # Esta linha vai funcionar quando o app estiver no Streamlit Community Cloud
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except (KeyError, FileNotFoundError):
    # Esta linha vai funcionar quando você rodar o app localmente
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configura a biblioteca do Gemini com a chave que encontramos
genai.configure(api_key=GEMINI_API_KEY)


# --- Configuração da Página ---
st.set_page_config(
    page_title="Gerador de Flashcards para Anki",
    page_icon="🧠",
    layout="centered"
)

# --- Título e Descrição ---
st.title("🧠 Gerador de Flashcards Mágico para Anki")
st.markdown("""
Cole suas anotações de aula ou o texto de um PDF abaixo, e a IA irá criar automaticamente
flashcards no formato Pergunta/Resposta, prontos para importar no Anki!
""")

# --- Interface do Usuário ---
input_text = st.text_area("Cole seu texto aqui:", height=250, placeholder="Ex: A capital do Brasil é Brasília. A fórmula da água é H2O...")

if st.button("Gerar Flashcards ✨"):
    if not GEMINI_API_KEY:
        st.error("Chave da API do Gemini não encontrada! Verifique seu arquivo .env ou os Secrets do Streamlit.")
    elif input_text:
        with st.spinner("Aguarde... A mágica está acontecendo..."):
            try:
                model = genai.GenerativeModel('gemini-1.5-pro-latest')
                
                prompt = f"""
                Aja como um especialista em criar materiais de estudo.
                Baseado no texto abaixo, extraia os conceitos chave e gere pares de Pergunta e Resposta no formato de flashcards.
                A pergunta deve ser clara e a resposta concisa.
                Formate a saída EXATAMENTE como: 'Pergunta;Resposta', com cada flashcard em uma nova linha.
                NÃO inclua cabeçalhos ou qualquer outro texto antes ou depois dos flashcards.

                TEXTO ORIGINAL:
                {input_text}
                """

                response = model.generate_content(prompt)
                flashcards_text = response.text

                data = StringIO(flashcards_text)
                df = pd.read_csv(data, sep=';', header=None)
                df.columns = ["Pergunta", "Resposta"]

                st.success("Flashcards gerados com sucesso!")
                st.dataframe(df)

                csv = df.to_csv(sep=';', index=False, header=False).encode('utf-8')

                st.download_button(
                   label="Baixar .csv para Anki",
                   data=csv,
                   file_name='flashcards_para_anki.csv',
                   mime='text/csv',
                )

            except Exception as e:
                st.error(f"Ocorreu um erro ao gerar os flashcards: {e}")
    else:

        st.warning("Por favor, insira um texto para gerar os flashcards.")

