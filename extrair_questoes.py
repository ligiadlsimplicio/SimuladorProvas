import pdfplumber
import os
import re
import json

PASTA_PDFS = "provas"
QUESTOES_JSON = []

def extrair_enunciado_e_alternativas(texto_questao):
    texto = texto_questao.replace("\r", "")
    # Padrão para capturar enunciado e as alternativas A, B, C, D e E
    padrao = r"(A[\)\.\-].*?)(B[\)\.\-].*?)(C[\)\.\-].*?)(D[\)\.\-].*?)(E[\)\.\-].*)"
    match = re.search(padrao, texto, re.S)
    if not match: return None

    enunciado = texto[:match.start()].strip()
    alternativas = {
        "A": match.group(1)[2:].strip(),
        "B": match.group(2)[2:].strip(),
        "C": match.group(3)[2:].strip(),
        "D": match.group(4)[2:].strip(),
        "E": match.group(5)[2:].strip(),
    }
    return enunciado, alternativas

for arquivo in os.listdir(PASTA_PDFS):
    if arquivo.endswith(".pdf"):
        caminho = os.path.join(PASTA_PDFS, arquivo)
        print(f"Lendo questões de: {arquivo}")
        with pdfplumber.open(caminho) as pdf:
            texto_completo = "\n".join([p.extract_text() or "" for p in pdf.pages])
            
        # Separa por "QUESTÃO XX"
        blocos = re.split(r"QUESTÃO\s+\d+", texto_completo)
        
        for i, bloco in enumerate(blocos[1:], start=1):
            res = extrair_enunciado_e_alternativas(bloco)
            if res:
                enunciado, alts = res
                QUESTOES_JSON.append({
                    "arquivo_origem": arquivo, # IMPORTANTE: agora sabemos de onde veio!
                    "numero": i,
                    "enunciado": enunciado,
                    "alternativas": alts,
                    "correta": None
                })

with open("questoes_tjsp.json", "w", encoding="utf-8") as f:
    json.dump(QUESTOES_JSON, f, ensure_ascii=False, indent=2)

print(f"✅ Sucesso! {len(QUESTOES_JSON)} questões salvas com identificação da prova.")