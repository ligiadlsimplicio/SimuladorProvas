import os
import re
import json

def identificar_materia(texto):
    t = texto.upper()
    if "LÍNGUA PORTUGUESA" in t or "PORTUGUESA" in t: return "Português"
    if "ATUALIDADES" in t: return "Atualidades / PCD"
    if "INFORMÁTICA" in t: return "Informática"
    if "RACIOCÍNIO LÓGICO" in t: return "Raciocínio Lógico"
    if "ESPECÍFICOS" in t or "SERVIÇO SOCIAL" in t: return "Serviço Social"
    return None

def processar_txt_para_json():
    todas_questoes = []
    
    # Procura arquivos TXT na pasta atual
    arquivos_limpos = [f for f in os.listdir('.') if f.startswith("LIMPO_") and f.endswith(".txt")]

    if not arquivos_limpos:
        print("❌ Nenhum arquivo que começa com 'LIMPO_' foi encontrado na pasta!")
        return

    for nome_arquivo in arquivos_limpos:
        print(f"📦 Lendo arquivo: {nome_arquivo}")
        with open(nome_arquivo, "r", encoding="utf-8") as f:
            conteudo = f.read()

        # Split mais flexível: Procura por [Número]. ou [Número].[Espaço]
        # O (?:^|\n) garante que pegamos o início do arquivo ou uma nova linha
        blocos = re.split(r'(?:^|\n)(?=\d{1,3}\.)', conteudo)
        
        materia_atual = "Conhecimentos Gerais"
        
        for bloco in blocos:
            if not bloco.strip(): continue

            # Detecta mudança de matéria
            nova_materia = identificar_materia(bloco)
            if nova_materia:
                materia_atual = nova_materia
            
            # Regex sniper: Pega número, enunciado e para quando achar (A) ou A)
            match = re.search(r'(\d{1,3})\.\s*(.*?)(?=\s*\(?[A-E][\)\.]\s+)', bloco, re.DOTALL)
            
            if match:
                num = int(match.group(1))
                enunciado = match.group(2).strip().replace('\n', ' ')
                
                # Captura alternativas (A) ou A) ou A.
                alts_raw = re.findall(r'\(?([A-E])\)[\.\s]+(.*?)(?=\s*\(?[A-E]\)|\n|$)', bloco, re.DOTALL)
                
                dic_alts = {letra.strip(): texto.strip().replace('\n', ' ') for letra, texto in alts_raw}
                
                # Se achou as alternativas, adiciona
                if len(dic_alts) >= 4:
                    todas_questoes.append({
                        "id_prova": nome_arquivo.replace("LIMPO_", "").replace(".txt", ".pdf"),
                        "materia": materia_atual,
                        "numero": num,
                        "enunciado": enunciado,
                        "alternativas": dic_alts,
                        "correta": None
                    })

    # Salva SEMPRE o arquivo, mesmo que vazio para não dar erro no próximo script
    with open("questoes_tjsp.json", "w", encoding="utf-8") as f:
        json.dump(todas_questoes, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Banco de dados criado com {len(todas_questoes)} questões.")

if __name__ == "__main__":
    processar_txt_para_json()