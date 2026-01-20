import pdfplumber
import os
import re
import json

PASTA_GABARITOS = "provas/gabaritos"

def carregar_questoes():
    with open("questoes_tjsp.json", "r", encoding="utf-8") as f:
        return json.load(f)

def extrair_respostas_gabarito(caminho_pdf):
    respostas = {}
    with pdfplumber.open(caminho_pdf) as pdf:
        texto = ""
        for p in pdf.pages:
            texto += p.extract_text() + "\n"
    
    # Busca o padrão "01-A" ou "1. C" ou "01 C"
    matches = re.findall(r"(\d{1,3})[\s\.\-]*([A-E])(?!\w)", texto)
    for num, letra in matches:
        respostas[int(num)] = letra
    return respostas

questoes = carregar_questoes()
gabaritos_processados = {}

# 1. Mapeia todos os gabaritos disponíveis
for arquivo in os.listdir(PASTA_GABARITOS):
    if arquivo.endswith(".pdf"):
        print(f"📖 Lendo Gabarito: {arquivo}")
        gabaritos_processados[arquivo] = extrair_respostas_gabarito(os.path.join(PASTA_GABARITOS, arquivo))

# 2. Automação do Cruzamento (Match)
print("\n🔗 Cruzando questões com gabaritos...")
for q in questoes:
    for nome_gabarito, mapa_respostas in gabaritos_processados.items():
        # LÓGICA DE MATCH: Se o ano (ex: 2017) ou o nome base da prova 
        # estiver no nome do arquivo do gabarito, eles dão "match"
        nome_prova_limpo = q['id_prova'].lower().replace(".pdf", "")
        nome_gabarito_limpo = nome_gabarito.lower().replace(".pdf", "")
        
        # Extrai o ano do nome do arquivo para facilitar o match (ex: 2017, 2025)
        ano_prova = re.search(r"\d{4}", nome_prova_limpo)
        
        if ano_prova and ano_prova.group() in nome_gabarito_limpo:
            match_encontrado = True
        elif nome_prova_limpo in nome_gabarito_limpo or nome_gabarito_limpo in nome_prova_limpo:
            match_encontrado = True
        else:
            match_encontrado = False

        if match_encontrado:
            if q['numero'] in mapa_respostas:
                q['correta'] = mapa_respostas[q['numero']]

# 3. Salva o resultado final
with open("questoes_tjsp.json", "w", encoding="utf-8") as f:
    json.dump(questoes, f, ensure_ascii=False, indent=2)

total_com_gabarito = len([q for q in questoes if q['correta'] is not None])
print(f"✅ Sucesso! {total_com_gabarito} questões agora possuem gabarito oficial.")