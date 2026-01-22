import fitz  # PyMuPDF
import os
import re

# Pega a pasta onde o script está rodando
DIRETORIO_ATUAL = os.getcwd()
PASTA_PROVAS = os.path.join(DIRETORIO_ATUAL, "provas")

def limpar_lixo(texto):
    if not texto: return ""
    lixo = [r"www\.pciconcursos\.com\.br", r"pcimarkpci.*", r"PODER JUDICIÁRIO.*", r"TRIBUNAL DE JUSTIÇA.*"]
    for padrao in lixo:
        texto = re.sub(padrao, "", texto, flags=re.IGNORECASE)
    return texto.strip()

def processar_pdf(caminho_pdf):
    nome_base = os.path.basename(caminho_pdf).replace(".pdf", ".txt")
    nome_saida = os.path.join(DIRETORIO_ATUAL, f"LIMPO_{nome_base}")
    
    doc = fitz.open(caminho_pdf)
    texto_final = []

    for pagina in doc:
        largura, altura = pagina.rect.width, pagina.rect.height
        caixa_esq = fitz.Rect(0, 50, largura/2, altura - 50)
        caixa_dir = fitz.Rect(largura/2, 50, largura, altura - 50)
        texto_pag = (pagina.get_text("text", clip=caixa_esq)) + "\n" + (pagina.get_text("text", clip=caixa_dir))
        texto_final.append(limpar_lixo(texto_pag))
    doc.close()
    
    with open(nome_saida, "w", encoding="utf-8") as f:
        f.write("\n".join(texto_final))
    print(f"✅ Arquivo criado em: {nome_saida}")

# Verifica se a pasta provas existe
if not os.path.exists(PASTA_PROVAS):
    print(f"❌ ERRO: A pasta '{PASTA_PROVAS}' não foi encontrada!")
else:
    for arquivo in os.listdir(PASTA_PROVAS):
        if arquivo.lower().endswith(".pdf"):
            processar_pdf(os.path.join(PASTA_PROVAS, arquivo))