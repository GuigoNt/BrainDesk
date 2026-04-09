import customtkinter as ctk
import ollama
import os
from database import adicionar_texto, buscar_contexto, listar_tudo, limpar_memoria, carregar_modelo
import uuid
import sys
import threading
from updater import verificar_update

# ================= CONFIG =================
materia_atual = "geral"
processando = False

# ================= PRELOAD =================
def preload():
    carregar_modelo()

threading.Thread(target=preload, daemon=True).start()

# Corrigir erro do PyInstaller
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")

# ================= CHAT UI =================
def adicionar_mensagem(texto, tipo="user"):
    frame = ctk.CTkFrame(resposta_frame, fg_color="transparent")
    frame.pack(fill="x", pady=5, padx=10)

    if tipo == "user":
        cor = "#E50914"
        anchor = "e"
        nome = "Você"
    else:
        cor = "#2b2b2b"
        anchor = "w"
        nome = "IA"

    label = ctk.CTkLabel(
        frame,
        text=f"{nome}: {texto}",
        wraplength=600,
        justify="left",
        fg_color=cor,
        corner_radius=10,
        padx=10,
        pady=6
    )

    label.pack(anchor=anchor)

# ================= INTELIGÊNCIA =================
def eh_pergunta(texto):
    texto = texto.lower()

    palavras_pergunta = [
        "o que", "como", "por que", "porque",
        "qual", "quando", "onde", "quem"
    ]

    if texto.endswith("?"):
        return True

    return any(texto.startswith(p) for p in palavras_pergunta)

# ================= PROCESSAMENTO =================
def processar():
    global processando

    if processando:
        return

    texto = entrada.get("1.0", "end").strip()

    if texto == "":
        return

    processando = True
    entrada.configure(state="disabled")

    entrada.delete("1.0", "end")

    def tarefa():
        global processando

        try:
            if eh_pergunta(texto):
                adicionar_mensagem(texto, "user")

                contexto = buscar_contexto(texto, materia_atual)

                prompt = f"""
                Baseado nesses estudos:
                {contexto}

                Responda de forma clara:
                {texto}
                """

                resposta_ia = ollama.chat(
                    model="llama3",
                    messages=[{"role": "user", "content": prompt}]
                )

                adicionar_mensagem(resposta_ia["message"]["content"], "ia")

            else:
                id_unico = str(uuid.uuid4())
                adicionar_texto(texto, id_unico, materia_atual)

                adicionar_mensagem(f"Salvo em '{materia_atual}' ✅", "ia")

        except Exception as e:
            adicionar_mensagem(f"Erro: {str(e)}", "ia")

        finally:
            processando = False
            entrada.configure(state="normal")

    threading.Thread(target=tarefa, daemon=True).start()

# ================= ENTER =================
def ao_pressionar_enter(event):
    if event.state & 0x1:  # SHIFT + ENTER
        return

    processar()
    return "break"

# ================= FUNÇÕES EXTRAS =================
def gerar_resumo():
    adicionar_mensagem("Gerar resumo", "user")

    def tarefa():
        contexto = buscar_contexto("resuma", materia_atual)

        resposta_ia = ollama.chat(
            model="llama3",
            messages=[{"role": "user", "content": f"Resuma:\n{contexto}"}]
        )

        adicionar_mensagem(resposta_ia["message"]["content"], "ia")

    threading.Thread(target=tarefa, daemon=True).start()

def gerar_questoes():
    adicionar_mensagem("Gerar questões", "user")

    def tarefa():
        contexto = buscar_contexto("perguntas", materia_atual)

        resposta_ia = ollama.chat(
            model="llama3",
            messages=[{"role": "user", "content": f"Crie perguntas:\n{contexto}"}]
        )

        adicionar_mensagem(resposta_ia["message"]["content"], "ia")

    threading.Thread(target=tarefa, daemon=True).start()

def gerar_flashcards():
    adicionar_mensagem("Gerar flashcards", "user")

    def tarefa():
        contexto = buscar_contexto("flashcards", materia_atual)

        resposta_ia = ollama.chat(
            model="llama3",
            messages=[{"role": "user", "content": f"Crie flashcards:\n{contexto}"}]
        )

        adicionar_mensagem(resposta_ia["message"]["content"], "ia")

    threading.Thread(target=tarefa, daemon=True).start()

def ver_historico():
    dados = listar_tudo(materia_atual)
    adicionar_mensagem(f"📜 Histórico:", "ia")
    adicionar_mensagem(dados, "ia")

def apagar_memoria():
    limpar_memoria(materia_atual)
    adicionar_mensagem(f"Memória apagada!", "ia")

def limpar():
    for widget in resposta_frame.winfo_children():
        widget.destroy()

# ================= UI =================
ctk.set_appearance_mode("dark")

app = ctk.CTk()
app.title("🧠 BrainDesk - Assistente IA")
app.geometry("1000x650")
app.configure(fg_color="#0f0f0f")

# 🔥 UPDATE EM BACKGROUND
threading.Thread(target=verificar_update, daemon=True).start()

COR_PRIMARIA = "#E50914"

container = ctk.CTkFrame(app)
container.pack(fill="both", expand=True)

# ===== SIDEBAR =====
sidebar = ctk.CTkFrame(container, width=220, fg_color="#141414")
sidebar.pack(side="left", fill="y")

logo = ctk.CTkLabel(
    sidebar,
    text="🧠 BrainDesk",
    font=("Arial", 20, "bold"),
    text_color=COR_PRIMARIA
)
logo.pack(pady=20)

def btn_sidebar(texto, comando):
    return ctk.CTkButton(
        sidebar,
        text=texto,
        command=comando,
        fg_color="transparent",
        hover_color="#222222",
        anchor="w"
    )

btn_sidebar("📌 Resumo", gerar_resumo).pack(fill="x", padx=10, pady=5)
btn_sidebar("❓ Questões", gerar_questoes).pack(fill="x", padx=10, pady=5)
btn_sidebar("🧠 Flashcards", gerar_flashcards).pack(fill="x", padx=10, pady=5)
btn_sidebar("📜 Histórico", ver_historico).pack(fill="x", padx=10, pady=5)
btn_sidebar("🧹 Limpar Memória", apagar_memoria).pack(fill="x", padx=10, pady=5)

ctk.CTkLabel(sidebar, text="").pack(expand=True)

btn_sidebar("🗑 Limpar Chat", limpar).pack(fill="x", padx=10, pady=10)

# ===== MAIN =====
main = ctk.CTkFrame(container)
main.pack(side="left", fill="both", expand=True)

entrada = ctk.CTkTextbox(main, height=100)
entrada.pack(padx=10, pady=10, fill="x")

entrada.bind("<Return>", ao_pressionar_enter)

resposta_frame = ctk.CTkScrollableFrame(main)
resposta_frame.pack(padx=10, pady=10, fill="both", expand=True)

app.mainloop()