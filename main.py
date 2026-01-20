import flet as ft
import json
import random
import os

def main(page: ft.Page):
    # Configurações de visual do App
    page.title = "Simulado TJ-SP - Assistente Social"
    page.theme_mode = "light"
    page.window_width = 450
    page.window_height = 800
    page.scroll = "auto"
    page.padding = 20

    # Carregar dados do JSON
    try:
        if not os.path.exists("questoes_tjsp.json"):
            page.add(ft.Text("Erro: Arquivo 'questoes_tjsp.json' não encontrado."))
            return
        with open("questoes_tjsp.json", "r", encoding="utf-8") as f:
            todas = json.load(f)
    except Exception as e:
        page.add(ft.Text(f"Erro ao ler arquivo: {e}"))
        return
    
    # Filtra apenas as questões que têm gabarito (suas 296 questões)
    questoes = [q for q in todas if q.get('correta') is not None]
    random.shuffle(questoes)

    state = {"indice": 0, "pontos": 0, "respondida": False}

    def verificar_resposta(e):
        if state["respondida"]: return
        state["respondida"] = True
        
        letra_clicada = e.control.data # Pegamos a letra salva no botão
        correta = questoes[state["indice"]]["correta"]
        
        if letra_clicada == correta:
            e.control.bgcolor = "green"
            e.control.color = "white"
            state["pontos"] += 1
            feedback_text.value = "✅ Resposta Correta!"
            feedback_text.color = "green"
        else:
            e.control.bgcolor = "red"
            e.control.color = "white"
            feedback_text.value = f"❌ Errada. A correta era {correta}"
            feedback_text.color = "red"
        
        btn_proxima.visible = True
        page.update()

    def proxima_questao(e):
        state["indice"] += 1
        state["respondida"] = False
        if state["indice"] < len(questoes) and state["indice"] < 10:
            montar_tela()
        else:
            mostrar_resultado()

    feedback_text = ft.Text("", size=18, weight="bold")
    
    # Botão Próxima usando o novo padrão "FilledButton"
    btn_proxima = ft.FilledButton(
        content=ft.Text("Próxima Questão"),
        on_click=proxima_questao, 
        visible=False
    )

    def montar_tela():
        page.clean()
        btn_proxima.visible = False
        feedback_text.value = ""
        q = questoes[state["indice"]]
        
        # Cabeçalho e Progresso
        page.add(
            ft.Text(f"Questão {state['indice'] + 1} de 10", size=16, weight="bold", color="blue"),
            ft.ProgressBar(value=(state['indice'] + 1) / 10, color="blue"),
            ft.Text(f"Matéria: {q.get('materia', 'Geral')}", size=12, italic=True),
            ft.Divider(),
        )

        # --- EXIBIÇÃO DE IMAGEM (Versão Blindada contra erros) ---
        if q.get("imagem") and os.path.exists(q["imagem"]):
            page.add(
                ft.Row(
                    [ft.Image(src=q["imagem"], width=350, fit="contain", border_radius=10)],
                    alignment="center" # Usamos texto puro para não dar erro de atributo
                )
            )

        # Enunciado
        page.add(
            ft.Text(q["enunciado"], size=16, weight="w500", text_align="justify"),
            ft.Text("\nSelecione uma alternativa:", size=14, italic=True),
        )

        # Botões das alternativas (Versão simplificada)
        for letra, texto in q["alternativas"].items():
            page.add(
                ft.ElevatedButton(
                    content=ft.Container(
                        content=ft.Text(f"{letra}) {texto}", size=14),
                        padding=15 # Espaço interno do botão
                    ),
                    data=letra,
                    on_click=verificar_resposta,
                    width=420,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))
                )
            )
        
        page.add(ft.Divider(), feedback_text, btn_proxima)
        page.update()

    def mostrar_resultado():
        page.clean()
        page.add(
            ft.Column(
                [
                    ft.Icon(name="emoji_events", size=100, color="amber"),
                    ft.Text("Fim do Simulado!", size=30, weight="bold"),
                    ft.Text(f"Você acertou {state['pontos']} de 10.", size=20),
                    ft.FilledButton(
                        content=ft.Text("Tentar Novamente"), 
                        on_click=lambda _: reinicio_total()
                    )
                ],
                horizontal_alignment="center"
            )
        )
        page.update()

    def reinicio_total():
        state["indice"] = 0
        state["pontos"] = 0
        random.shuffle(questoes)
        montar_tela()

    # Iniciar o simulado
    montar_tela()

# Nas versões novas o comando é run() em vez de app()
if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")