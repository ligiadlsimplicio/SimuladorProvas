import fitz  # PyMuPDF
import os
import re
import json

PASTA_GABARITOS = "provas/gabaritos"

def carregar_questoes():
    if not os.path.exists("questoes_tjsp.json"):
        return []
    with open("questoes_tjsp.json", "r", encoding="utf-8") as f:
        return json.load(f)

def extrair_respostas_gabarito(caminho_pdf):
    respostas = {}
    doc = fitz.open(caminho_pdf)
    texto = ""
    for pagina in doc:
        texto += pagina.get_text()
    doc.close()
    
    # Busca o padrão "01-A" ou "1. C" ou "01 C"
    matches = re.findall(r"(\d{1,3})[\s\.\-]*([A-E])(?!\w)", texto)
    for num, letra in matches:
        respostas[int(num)] = letra
    return respostas

questoes = carregar_questoes()
if not questoes:
    print("❌ Erro: O arquivo 'questoes_tjsp.json' não existe. Rode o 'gerar_banco_questoes.py' primeiro!")
    exit()

gabaritos_processados = {}

# 1. Mapeia todos os gabaritos disponíveis
if not os.path.exists(PASTA_GABARITOS):
    print(f"❌ Erro: Pasta {PASTA_GABARITOS} não encontrada!")
    exit()

for arquivo in os.listdir(PASTA_GABARITOS):
    if arquivo.endswith(".pdf"):
        print(f"📖 Lendo Gabarito: {arquivo}")
        gabaritos_processados[arquivo] = extrair_respostas_gabarito(os.path.join(PASTA_GABARITOS, arquivo))

# 2. Automação do Cruzamento (Match)
print("\n🔗 Cruzando questões com gabaritos...")
total_atualizado = 0

for q in questoes:
    for nome_gabarito, mapa_respostas in gabaritos_processados.items():
        # Lógica de Match pelo ano ou nome do arquivo
        nome_prova = q['id_prova'].lower()
        nome_gabarito_limpo = nome_gabarito.lower()
        
        # Tenta achar o ano (2017, 2025, etc)
        ano_match = re.search(r"\d{4}", nome_prova)
        if ano_match and ano_match.group() in nome_gabarito_limpo:
            if q['numero'] in mapa_respostas:
                q['correta'] = mapa_respostas[q['numero']]
                total_atualizado += 1

# 3. Salva o resultado final
with open("questoes_tjsp.json", "w", encoding="utf-8") as f:
    json.dump(questoes, f, ensure_ascii=False, indent=2)

print(f"✅ Sucesso! Gabaritos aplicados a {total_atualizado} questões.")