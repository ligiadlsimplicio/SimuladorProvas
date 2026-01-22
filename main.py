import flet as ft
import json
import random
import os

def main(page: ft.Page):
    # Configurações de página
    page.title = "Simulado TJ-SP"
    page.theme_mode = "light"
    page.padding = 20
    page.scroll = "auto"
    page.horizontal_alignment = "center"

    state = {
        "banco": [],
        "questoes": [],
        "indice": 0,
        "pontos": 0,
        "respondida": False
    }

    # 1. Carregar Banco de Dados
    try:
        if os.path.exists("questoes_tjsp.json"):
            with open("questoes_tjsp.json", "r", encoding="utf-8") as f:
                state["banco"] = json.load(f)
        else:
            page.add(ft.Text("Arquivo JSON não encontrado!"))
            return
    except Exception as e:
        page.add(ft.Text(f"Erro ao carregar: {e}"))
        return

    def validar_resposta(e):
        # Se já respondeu, ignora novos cliques
        if state["respondida"]: 
            return
        
        state["respondida"] = True
        letra_clicada = e.control.data
        correta = state["questoes"][state["indice"]]["correta"]
        
        print(f"DEBUG: Você clicou na {letra_clicada}. A correta é {correta}")

        if letra_clicada == correta:
            e.control.bgcolor = "green"
            e.control.color = "white"
            state["pontos"] += 1
        else:
            e.control.bgcolor = "red"
            e.control.color = "white"

        # Mostra o botão de próxima
        btn_proxima.visible = True
        page.update()

    def ir_proxima(e):
        state["indice"] += 1
        state["respondida"] = False
        if state["indice"] < len(state["questoes"]) and state["indice"] < 10:
            mostrar_pergunta()
        else:
            mostrar_fim()

    # Botão Próxima (Centralizado)
    btn_proxima = ft.FilledButton(
        content=ft.Text("PRÓXIMA QUESTÃO", weight="bold"),
        on_click=ir_proxima,
        visible=False,
        width=300,
        height=50
    )

    def iniciar_simulado(materia=None):
        if materia:
            state["questoes"] = [q for q in state["banco"] if q.get("materia") == materia and q.get("correta")]
        else:
            state["questoes"] = [q for q in state["banco"] if q.get("correta")]
        
        if not state["questoes"]: return

        random.shuffle(state["questoes"])
        state["indice"] = 0
        state["pontos"] = 0
        state["respondida"] = False
        mostrar_pergunta()

    def mostrar_menu():
        page.clean()
        page.add(
            ft.Text("SIMULADO TJ-SP", size=32, weight="bold", color="blue"),
            ft.Text("Assistente Social", size=20, color="grey"),
            ft.Divider(height=40),
            ft.FilledButton(
                content=ft.Text("INICIAR SIMULADO GERAL", size=16),
                width=400, height=60, on_click=lambda _: iniciar_simulado()
            ),
            ft.Container(height=10),
            ft.OutlinedButton(
                content=ft.Text("SÓ SERVIÇO SOCIAL", size=16),
                width=400, height=60, on_click=lambda _: iniciar_simulado("Serviço Social")
            ),
            ft.Container(height=10),
            ft.OutlinedButton(
                content=ft.Text("SÓ PORTUGUÊS", size=16),
                width=400, height=60, on_click=lambda _: iniciar_simulado("Português")
            ),
            ft.Divider(height=40),
            ft.Text(f"Questões disponíveis: {len(state['banco'])}", italic=True)
        )
        page.update()

    def mostrar_pergunta():
        page.clean()
        btn_proxima.visible = False
        q = state["questoes"][state["indice"]]
        
        page.add(
            ft.Text(f"QUESTÃO {state['indice'] + 1} DE 10", size=18, weight="bold"),
            ft.ProgressBar(value=(state['indice'] + 1) / 10, color="blue"),
            ft.Divider(),
            ft.Text(q["enunciado"], size=16, text_align="justify"),
            ft.Container(height=20)
        )

        # Alternativas (Usando FilledTonalButton para cliques mais firmes)
        for letra, texto in q["alternativas"].items():
            page.add(
                ft.FilledTonalButton(
                    content=ft.Text(f"{letra}) {texto}", size=15, text_align="left"),
                    data=letra,
                    on_click=validar_resposta,
                    width=420,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                        padding=15
                    )
                ),
                ft.Container(height=5)
            )
        
        page.add(ft.Divider(), btn_proxima)
        page.update()

    def mostrar_fim():
        page.clean()
        page.add(
            ft.Icon("emoji_events", size=100, color="amber"),
            ft.Text("FIM DO SIMULADO", size=30, weight="bold"),
            ft.Text(f"Você acertou {state['pontos']} de 10.", size=22),
            ft.Container(height=30),
            ft.FilledButton(
                content=ft.Text("VOLTAR AO INÍCIO"), 
                on_click=lambda _: mostrar_menu(),
                width=300, height=50
            )
        )
        page.update()

    mostrar_menu()

# Execução padrão 0.80+
if __name__ == "__main__":
    ft.run(main, assets_dir="assets")