import flet as ft
import json
import os
import random

def main(page: ft.Page):
    page.title = "SIMULADOR TJ-SP"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#F0F2F5"
    page.scroll = "auto"
    page.horizontal_alignment = "center" 

    state = {
        "banco": [],
        "questoes": [],
        "indice": 0,
        "pontos": 0,
        "respondida": False,
        "total": 10
    }

    # Carregar Banco de Dados
    if os.path.exists("questoes_tjsp.json"):
        with open("questoes_tjsp.json", "r", encoding="utf-8") as f:
            state["banco"] = json.load(f)
    else:
        page.add(ft.Text("Erro: arquivo JSON não encontrado!"))
        return

    label_feedback = ft.Text("", size=18, weight="bold", text_align="center")

    def verificar_resposta(e):
        if state["respondida"]: return
        state["respondida"] = True
        letra_clicada = e.control.data
        correta = state["questoes"][state["indice"]]["correta"]
        
        if letra_clicada == correta:
            e.control.bgcolor = "green"
            e.control.color = "white"
            label_feedback.value = "✅ ACERTOU!"
            label_feedback.color = "green"
            state["pontos"] += 1
        else:
            e.control.bgcolor = "red"
            e.control.color = "white"
            label_feedback.value = f"❌ ERROU! A correta era {correta}"
            label_feedback.color = "red"
        
        btn_proxima.visible = True
        page.update()

    def ir_proxima(e):
        state["indice"] += 1
        state["respondida"] = False
        if state["indice"] < state["total"]:
            mostrar_pergunta()
        else:
            mostrar_fim()

    btn_proxima = ft.FilledButton(
        content=ft.Text("PRÓXIMA QUESTÃO", weight="bold"), 
        on_click=ir_proxima, 
        visible=False,
        width=300, height=50
    )

    def iniciar(materia=None):
        if materia:
            state["questoes"] = [q for q in state["banco"] if q.get("materia") == materia and q.get("correta")]
        else:
            state["questoes"] = [q for q in state["banco"] if q.get("correta")]
        
        if len(state["questoes"]) == 0: return
        
        random.shuffle(state["questoes"])
        state["indice"] = 0
        state["pontos"] = 0
        mostrar_pergunta()

    def mostrar_menu():
        page.clean()
        menu_items = ft.Container(
            content=ft.Column([
                ft.Text("🎓", size=60),
                ft.Text("TJ-SP SIMULADOR", size=32, weight="bold", color="blue"),
                ft.Text("Assistente Social Judiciário", size=18, color="grey700"),
                ft.Divider(height=40),
                ft.FilledButton(content=ft.Text("🔥 SIMULADO GERAL (10 questões)"), width=400, height=60, on_click=lambda _: iniciar()),
                ft.Container(height=5),
                ft.FilledTonalButton(content=ft.Text("📚 SÓ SERVIÇO SOCIAL"), width=400, height=50, on_click=lambda _: iniciar("Serviço Social")),
                ft.FilledTonalButton(content=ft.Text("✍️ SÓ PORTUGUÊS"), width=400, height=50, on_click=lambda _: iniciar("Português")),
                ft.FilledTonalButton(content=ft.Text("💻 SÓ INFORMÁTICA"), width=400, height=50, on_click=lambda _: iniciar("Informática")),
                ft.Divider(height=40),
                ft.Text(f"Total: {len(state['banco'])} questões extraídas", size=12, italic=True),
            ], horizontal_alignment="center"),
            width=700, bgcolor="white", padding=40, border_radius=20, shadow=ft.BoxShadow(blur_radius=15, color="black12")
        )
        page.add(ft.Container(height=20), menu_items)
        page.update()

    def mostrar_pergunta():
        page.clean()
        btn_proxima.visible = False
        label_feedback.value = ""
        q = state["questoes"][state["indice"]]
        
        quadro_questao = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.TextButton(content=ft.Text("🏠 Início"), on_click=lambda _: mostrar_menu()),
                    ft.Text(f"Questão {state['indice']+1}/10", weight="bold")
                ], alignment="spaceBetween"),
                ft.ProgressBar(value=(state['indice']+1)/10, color="blue"),
                ft.Text(f"Matéria: {q['materia']}", size=11, italic=True, color="blue"),
                ft.Divider(),
                ft.Text(q["enunciado"], size=16, text_align="justify"),
                ft.Container(height=10),
            ]),
            width=750, padding=30, bgcolor="white", border_radius=15, shadow=ft.BoxShadow(blur_radius=10, color="black12")
        )

        # Suporte a Imagens (verifica se existe imagem e arquivo)
        if q.get("imagem") and os.path.exists(os.path.join("assets", q["imagem"])):
            quadro_questao.content.controls.insert(4, ft.Row([
                ft.Image(src=q["imagem"], width=400, fit="contain", border_radius=10)
            ], alignment="center"))

        # Alternativas (CORRIGIDO: no_wrap=False em vez de soft_wrap)
        for letra, texto in q["alternativas"].items():
            quadro_questao.content.controls.append(
                ft.OutlinedButton(
                    content=ft.Container(
                        content=ft.Text(f"{letra}) {texto}", size=14, no_wrap=False), # Aqui estava o erro!
                        padding=ft.padding.symmetric(vertical=12, horizontal=10),
                    ),
                    data=letra, 
                    on_click=verificar_resposta, 
                    width=680,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))
                )
            )
        
        quadro_questao.content.controls.extend([
            ft.Divider(), 
            ft.Row([label_feedback], alignment="center"), 
            ft.Row([btn_proxima], alignment="center")
        ])

        page.add(ft.Container(height=20), quadro_questao, ft.Container(height=40))
        page.update()

    def mostrar_fim():
        page.clean()
        page.add(
            ft.Container(height=40),
            ft.Container(
                content=ft.Column([
                    ft.Text("🏆", size=80),
                    ft.Text("FIM DO SIMULADO", size=30, weight="bold"),
                    ft.Text(f"Você acertou {state['pontos']} de 10.", size=22),
                    ft.Container(height=20),
                    ft.FilledButton(content=ft.Text("RECOMEÇAR"), on_click=lambda _: mostrar_menu(), width=300, height=50)
                ], horizontal_alignment="center"),
                width=500, bgcolor="white", padding=50, border_radius=20, shadow=ft.BoxShadow(blur_radius=15, color="black12")
            )
        )
        page.update()

    mostrar_menu()

if __name__ == "__main__":
    ft.run(main, assets_dir="assets")