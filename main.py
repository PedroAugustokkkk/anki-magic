# Importa as bibliotecas necessárias
import streamlit as st
import google.generativeai as genai
import pandas as pd
from io import StringIO
import os
from dotenv import load_dotenv
import PyPDF2  # Biblioteca para ler PDFs
from PIL import Image  # Biblioteca para abrir imagens
import pytesseract  # Biblioteca para extrair texto de imagens (OCR)

# --- Carregando a Chave da API ---
load_dotenv()
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except (KeyError, FileNotFoundError):
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# --- Funções de Extração de Texto ---

# Função para extrair texto de um arquivo PDF
def extract_text_from_pdf(pdf_file):
    # Cria um objeto leitor de PDF
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    # Inicializa uma variável para armazenar todo o texto
    text = ""
    # Itera sobre cada página do PDF
    for page in pdf_reader.pages:
        # Extrai o texto da página e o adiciona à nossa variável
        text += page.extract_text()
    return text

# Função para extrair texto de um arquivo de imagem
def extract_text_from_image(image_file):
    # Abre o arquivo de imagem usando a biblioteca Pillow
    img = Image.open(image_file)
    # Usa o Tesseract para extrair o texto da imagem
    # 'lang="por"' tenta usar o dicionário de português para melhor precisão
    text = pytesseract.image_to_string(img, lang='por')
    return text

# --- Configuração da Página ---
st.set_page_config(
    page_title="Gerador de Flashcards para Anki",
    page_icon="🧠",
    layout="centered"
)

# --- Título e Descrição ---
st.title("🧠 Gerador de Flashcards Mágico para Anki")
st.markdown("""
Use a IA para criar flashcards de forma automática a partir de suas anotações, PDFs ou até mesmo imagens (este último em manutenção)!
""")

# --- Interface com Abas ---
# Cria as abas para cada tipo de entrada
tab1, tab2, tab3 = st.tabs(["📝 Digitar Texto", "📄 Enviar PDF", "🖼️ Enviar Imagem"])

# Inicializa a variável que guardará o texto extraído
extracted_text = None

# Conteúdo da Aba 1: Digitar Texto
with tab1:
    st.header("Cole seu texto diretamente aqui")
    text_input = st.text_area("Texto de entrada", height=250, label_visibility="collapsed")
    if text_input:
        extracted_text = text_input

# Conteúdo da Aba 2: Enviar PDF
with tab2:
    st.header("Faça o upload de um arquivo PDF")
    pdf_file = st.file_uploader("Escolha um arquivo PDF", type="pdf", label_visibility="collapsed")
    if pdf_file:
        with st.spinner("Lendo o PDF..."):
            extracted_text = extract_text_from_pdf(pdf_file)

# Conteúdo da Aba 3: Enviar Imagem
with tab3:
    st.header("Faça o upload de uma imagem (PNG, JPG)")
    image_file = st.file_uploader("Escolha uma imagem", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
    if image_file:
        with st.spinner("Lendo a imagem (OCR)..."):
            extracted_text = extract_text_from_image(image_file)

# --- Lógica de Geração dos Flashcards ---

# O botão de gerar agora fica fora das abas
if st.button("Gerar Flashcards ✨"):
    if not GEMINI_API_KEY:
        st.error("Chave da API do Gemini não encontrada!")
    elif extracted_text:  # Verifica se algum texto foi extraído de qualquer uma das fontes
        with st.spinner("Aguarde... A IA está criando seus flashcards..."):
            try:
                model = genai.GenerativeModel('gemini-2.5-pro')
                prompt = f"""
                Aja como um especialista em criar materiais de estudo diretamente para estudantes de escolas, cursos técnicos e faculdade.
                Baseado no texto abaixo, extraia os conceitos chave e gere pares de Pergunta e Resposta no formato de flashcards.
                A pergunta deve ser clara e a resposta concisa.
                Formate a saída EXATAMENTE como: 'Pergunta;Resposta', com cada flashcard em uma nova linha.
                NÃO inclua cabeçalhos ou qualquer outro texto antes ou depois dos flashcards.

                TEXTO ORIGINAL:
                {extracted_text}
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
        st.warning("Por favor, insira um texto, PDF ou imagem para gerar os flashcards.")

