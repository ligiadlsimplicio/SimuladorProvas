import pdfplumber
import os
import re
import json

PASTA_GABARITOS = "provas/gabaritos"
mapeamento_gabaritos = {}

for arquivo in os.listdir(PASTA_GABARITOS):
    if arquivo.endswith(".pdf"):
        caminho = os.path.join(PASTA_GABARITOS, arquivo)
        print(f"Extraindo gabarito de: {arquivo}")
        
        with pdfplumber.open(caminho) as pdf:
            texto = "\n".join([p.extract_text() or "" for p in pdf.pages])
            
        # Procura padrões como "1 - A", "01. B", "1 B"
        respostas = re.findall(r"(\d{1,3})\s*[\-\.\s]\s*([A-E])", texto)
        
        # Cria um dicionário para esta prova {1: 'A', 2: 'C'...}
        # Tenta associar o nome do gabarito ao nome da prova (ajuste o nome se necessário)
        nome_prova_relacionada = arquivo.replace("gabarito_", "").replace("gabarito ", "")
        mapeamento_gabaritos[arquivo] = {int(n): r for n, r in respostas}

# Agora, vamos atualizar o questoes_tjsp.json com as respostas certas
with open("questoes_tjsp.json", "r", encoding="utf-8") as f:
    questoes = json.load(f)

print("Cruzando dados...")
for q in questoes:
    # Aqui fazemos uma lógica simples: se o nome do arquivo da prova estiver 
    # contido no nome do arquivo do gabarito (ou vice-versa), ele tenta parear
    for nome_gab, mapa in mapeamento_gabaritos.items():
        # Verificação básica de nome (ex: se "2017" está no gabarito e na prova)
        if any(ano in q['arquivo_origem'] and ano in nome_gab for ano in ["2012", "2017", "2021", "2025"]):
            if q['numero'] in mapa:
                q['correta'] = mapa[q['numero']]

with open("questoes_tjsp.json", "w", encoding="utf-8") as f:
    json.dump(questoes, f, ensure_ascii=False, indent=2)

print("✅ Gabaritos aplicados ao arquivo de questões!")