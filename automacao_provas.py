import pdfplumber
import os
import re
import json

PASTA_PROVAS = "provas"
PASTA_ASSETS = "assets"

def identificar_materia(numero):
    if 1 <= numero <= 24: return "Português"
    if 25 <= numero <= 40: return "Direito / Atualidades"
    if 41 <= numero <= 70: return "Serviço Social (Específicas)"
    if 71 <= numero <= 80: return "Raciocínio Lógico"
    if 81 <= numero <= 100: return "Informática"
    return "Geral"

def limpar_texto(texto):
    if not texto: return ""
    # Limpa lixo eletrônico do PCI Concursos
    texto = re.sub(r"www\.pciconcursos\.com\.br|pcimarkpci.*|\(cid:\d+\)", "", texto)
    texto = re.sub(r"[A-Za-z0-9+/=]{30,}", "", texto) 
    return texto.strip()

def extrair_dados_pdf(caminho_pdf):
    questoes_da_prova = []
    nome_arquivo = os.path.basename(caminho_pdf)
    texto_apoio_acumulado = ""
    
    with pdfplumber.open(caminho_pdf) as pdf:
        for i, pagina in enumerate(pdf.pages):
            largura, altura = pagina.width, pagina.height
            
            # --- NOVA LÓGICA DE IMAGEM (MAIS SIMPLES) ---
            imagem_path = None
            texto_da_pagina = pagina.extract_text() or ""
            
            # Gatilhos: se tiver alguma dessas palavras, vamos procurar imagem com vontade
            gatilhos = ["charge", "tira", "quadrinho", "imagem", "leia", "considere", "abaixo", "figura"]
            tem_gatilho = any(g in texto_da_pagina.lower() for g in gatilhos)

            if pagina.images:
                # Filtramos imagens que estão muito no topo (logos) ou muito no fundo (rodapé)
                # E que tenham um tamanho mínimo de uma tirinha (largura > 150)
                imgs_validas = [
                    img for img in pagina.images 
                    if img['top'] > 50 and img['bottom'] < (altura - 50) and img['width'] > 150
                ]
                
                if imgs_validas and tem_gatilho:
                    try:
                        # Pega a maior imagem encontrada na área útil da página
                        maior_img = sorted(imgs_validas, key=lambda x: x['width']*x['height'], reverse=True)[0]
                        bbox = (maior_img["x0"], maior_img["top"], maior_img["x1"], maior_img["bottom"])
                        
                        # Tiramos o print da região da imagem com uma margem extra
                        # para garantir que pegamos o texto da tirinha também
                        margem = 15
                        caixa_print = (
                            max(0, maior_img["x0"] - margem), 
                            max(0, maior_img["top"] - margem), 
                            min(largura, maior_img["x1"] + margem), 
                            min(altura, maior_img["bottom"] + margem)
                        )
                        
                        img_obj = pagina.within_bbox(caixa_print).to_image(resolution=150)
                        nome_img = f"img_{nome_arquivo.replace('.pdf','')}_p{i}.png"
                        imagem_path = os.path.join(PASTA_ASSETS, nome_img)
                        img_obj.save(imagem_path)
                        print(f"📸 Imagem capturada na página {i} de {nome_arquivo}")
                    except: pass

            # --- EXTRAÇÃO DE TEXTO ---
            esq = pagina.crop((0, 0, largura/2, altura)).extract_text() or ""
            dire = pagina.crop((largura/2, 0, largura, altura)).extract_text() or ""
            texto_limpo = limpar_texto(esq + "\n" + dire)

            # Texto de apoio (Leia o texto...)
            apoio = re.search(r"(Leia o texto.*?para responder.*?$|Considere o texto.*?$)", texto_limpo, re.IGNORECASE | re.MULTILINE)
            if apoio: texto_apoio_acumulado = apoio.group(0)

            # Separação das questões
            matches = re.findall(r"(\d{1,3})\.\s*(.*?)(?=A\)\s+|B\)\s+|[A-E]\)\s+|$)", texto_limpo, re.DOTALL)
            questoes_brutas = re.split(r"\n(?=\d{1,3}\.\s)", texto_limpo)

            for q_bruta in questoes_brutas:
                match_header = re.match(r"(\d{1,3})\.\s*(.*?)(?=A\)\s)", q_bruta, re.DOTALL)
                if match_header:
                    num = int(match_header.group(1))
                    enunciado = match_header.group(2).strip().replace('\n', ' ')
                    
                    if num < 30 and texto_apoio_acumulado and "leia" not in enunciado.lower():
                        enunciado = f"{texto_apoio_acumulado}\n\n{enunciado}"

                    alts = re.findall(r"([A-E])\)\s*(.*?)(?=[A-E]\)\s+|$)", q_bruta, re.DOTALL)
                    dic_alts = {l.strip(): t.strip().replace('\n', ' ') for l, t in alts}

                    if len(dic_alts) >= 4:
                        # Vincula a imagem se ela estiver na mesma página da questão
                        # Ou se for uma das primeiras questões (onde tirinhas aparecem)
                        vincular = imagem_path if (num < 15 or "imagem" in enunciado.lower() or "charge" in enunciado.lower()) else None
                        
                        questoes_da_prova.append({
                            "id_prova": nome_arquivo,
                            "materia": identificar_materia(num),
                            "numero": num,
                            "enunciado": enunciado,
                            "alternativas": dic_alts,
                            "imagem": vincular,
                            "correta": None
                        })
    return questoes_da_prova

# Main
if not os.path.exists(PASTA_ASSETS): os.makedirs(PASTA_ASSETS)
todas = []
for arquivo in os.listdir(PASTA_PROVAS):
    if arquivo.endswith(".pdf"):
        print(f"🔍 Analisando Prova: {arquivo}")
        todas.extend(extrair_dados_pdf(os.path.join(PASTA_PROVAS, arquivo)))

with open("questoes_tjsp.json", "w", encoding="utf-8") as f:
    json.dump(todas, f, ensure_ascii=False, indent=2)
print("✅ Concluído! Se o terminal mostrou ícones de câmera (📸), as imagens foram salvas.")