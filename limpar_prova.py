import json
import re

def limpar_texto(texto):
    # Remove marcas d'água do PCI Concursos e cabeçalhos chatos
    linhas = texto.split('\n')
    linhas_limpas = []
    
    for linha in linhas:
        # Pula linhas que contêm as marcas de lixo que você viu
        if "pcimarkpci" in linha or "www.pciconcursos.com.br" in linha:
            continue
        if "PODER JUDICIÁRIO" in linha or "TRIBUNAL DE JUSTIÇA" in linha:
            continue
        if "Confidencial até o momento" in linha:
            continue
        linhas_limpas.append(linha)
    
    return "\n".join(linhas_limpas)

# Carrega o JSON que você já tem para limpar o conteúdo dele
with open("questoes_tjsp.json", "r", encoding="utf-8") as f:
    questoes = json.load(f)

for q in questoes:
    q['enunciado'] = limpar_texto(q['enunciado'])
    for letra in q['alternativas']:
        q['alternativas'][letra] = limpar_texto(q['alternativas'][letra])

# Salva de novo, agora limpinho
with open("questoes_tjsp.json", "w", encoding="utf-8") as f:
    json.dump(questoes, f, ensure_ascii=False, indent=2)

print("✨ JSON limpo com sucesso! Agora os enunciados estão sem aquele lixo eletrônico.")