# backend/main.py
from fastapi import FastAPI, UploadFile, File
import fitz  # PyMuPDF
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configuração para permitir que o Frontend converse com o Backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Em produção, mudaremos isso
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "API do Leitor de Editais está online!"}

@app.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    # Aqui entraremos com a lógica do PyMuPDF depois
    # Por enquanto, só vamos ler o nome do arquivo para testar
    doc = fitz.open(stream=await file.read(), filetype="pdf")
    num_paginas = doc.page_count
    return {
        "filename": file.filename,
        "paginas": num_paginas,
        "status": "PDF recebido com sucesso"
    }

# Para rodar: uvicorn main:app --reload