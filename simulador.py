import json
import random
import os

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

def rodar():
    with open("questoes_tjsp.json", "r", encoding="utf-8") as f:
        questoes = json.load(f)
    
    # Filtra apenas as que têm gabarito (no seu caso, todas as 154!)
    questoes = [q for q in questoes if q['correta'] is not None]
    random.shuffle(questoes)
    
    pontos = 0
    total_perguntas = 10 # Você pode mudar esse número para quanto quiser treinar

    for i, q in enumerate(questoes[:total_perguntas], 1):
        limpar_tela()
        print(f"=== SIMULADO TJ-SP | Questão {i}/{total_perguntas} ===")
        print(f"Prova de Origem: {q['id_prova']}\n")
        print(q['enunciado'])
        print("-" * 30)
        
        for letra, texto in q['alternativas'].items():
            print(f"{letra}) {texto}")
        
        resp = input("\nSua resposta (A, B, C, D ou E): ").strip().upper()
        
        if resp == q['correta']:
            print("\n✅ ACERTOU! Parabéns.")
            pontos += 1
        else:
            print(f"\n❌ ERROU. A correta era a letra [{q['correta']}].")
        
        input("\nPressione ENTER para continuar...")

    limpar_tela()
    print("=== RESULTADO FINAL ===")
    print(f"Você acertou {pontos} de {total_perguntas} questões.")
    print(f"Aproveitamento: {(pontos/total_perguntas)*100}%")
    print("=======================")

if __name__ == "__main__":
    rodar()