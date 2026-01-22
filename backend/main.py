import fitz  # PyMuPDF
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import io

app = FastAPI()

# Configuração de CORS (Para o Frontend conseguir falar com o Backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, trocaremos pelo link do site real
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "API do Leitor de Editais está ONLINE!"}

@app.post("/upload/")
async def upload_pdf(file: UploadFile = File(...)):
    # Verifica se é um PDF
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="O arquivo deve ser um PDF.")

    try:
        # Lê o arquivo da memória
        contents = await file.read()
        pdf_document = fitz.open(stream=contents, filetype="pdf")
        
        # Extrai texto simples para teste
        texto_completo = ""
        for pagina in pdf_document:
            texto_completo += pagina.get_text()

        return {
            "filename": file.filename,
            "total_paginas": pdf_document.page_count,
            "preview_texto": texto_completo[:500] + "..." # Mostra só os primeiros 500 caracteres
        }
    except Exception as e:
        return {"erro": str(e)}