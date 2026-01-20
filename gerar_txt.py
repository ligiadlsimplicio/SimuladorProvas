import pdfplumber
import os

PASTA_PDFS = "provas"
txt_path = "prova.txt"

texto = ""

for arquivo in os.listdir(PASTA_PDFS):
    if arquivo.lower().endswith(".pdf"):
        caminho_pdf = os.path.join(PASTA_PDFS, arquivo)
        print(f"📄 Lendo: {arquivo}")

        with pdfplumber.open(caminho_pdf) as pdf:
            for pagina in pdf.pages:
                conteudo = pagina.extract_text()
                if conteudo:
                    texto += conteudo + "\n"

with open(txt_path, "w", encoding="utf-8") as f:
    f.write(texto)

print("✅ Arquivo prova.txt criado com sucesso!")
