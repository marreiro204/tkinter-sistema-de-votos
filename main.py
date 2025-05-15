import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import os

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime

candidatos = []
votacao_ativa = False
matriculas_votantes = set()

CAMINHO_IMG = "img"  # Pasta onde as imagens estão

def mostrar_menu():
    janela.geometry("400x300")
    janela.configure(padx=20, pady=20)

    frame = tk.Frame(janela)
    frame.pack()

    tk.Label(frame, text="Escolha uma opção", font=("Arial", 14)).pack(pady=10)

    botoes = [
        ("Cadastro de candidato", cadastro_candidato),
        ("Iniciar votação", iniciar_votacao),
        ("Encerrar votação", encerrar_votacao)
    ]

    for texto, comando in botoes:
        tk.Button(frame, text=texto, command=comando, width=25).pack(pady=5)

def cadastro_candidato():
    janela_cadastro = tk.Toplevel(janela)
    janela_cadastro.title("Cadastro de candidato")
    janela_cadastro.geometry("400x400")

    dados = {
        "numero": tk.StringVar(),
        "nome": tk.StringVar(),
        "partido": tk.StringVar(),
        "foto_nome": tk.StringVar()
    }

    def escolher_foto():
        caminho = filedialog.askopenfilename(
            initialdir=CAMINHO_IMG,
            title="Escolha a foto do candidato",
            filetypes=[("Imagens", "*.png *.jpg *.jpeg")]
        )
        if caminho and CAMINHO_IMG in caminho:
            nome_arquivo = os.path.basename(caminho)
            dados["foto_nome"].set(nome_arquivo)
        else:
            messagebox.showerror("Erro", "A imagem deve estar na pasta 'img'.")

    campos = [("Número", "numero"), ("Nome", "nome"), ("Partido", "partido")]
    for label, chave in campos:
        tk.Label(janela_cadastro, text=f"{label} do candidato:").pack(pady=5)
        tk.Entry(janela_cadastro, textvariable=dados[chave]).pack(pady=5)

    tk.Button(janela_cadastro, text="Escolher foto", command=escolher_foto).pack(pady=10)
    tk.Label(janela_cadastro, textvariable=dados["foto_nome"]).pack(pady=5)

    def salvar_candidato():
        numero = dados["numero"].get().strip()
        nome = dados["nome"].get().strip()
        partido = dados["partido"].get().strip()
        foto_nome = dados["foto_nome"].get().strip()

        if not numero or not nome or not partido or not foto_nome:
            messagebox.showwarning("Erro", "Todos os campos devem ser preenchidos.")
            return

        if any(c["numero"] == numero for c in candidatos):
            messagebox.showerror("Erro", "Número de candidato já cadastrado.")
            return

        candidatos.append({
            "numero": numero,
            "nome": nome,
            "partido": partido,
            "votos": 0,
            "foto": foto_nome
        })

        messagebox.showinfo("Sucesso", "Candidato cadastrado com sucesso!")
        janela_cadastro.destroy()

    tk.Button(janela_cadastro, text="Salvar", command=salvar_candidato).pack(pady=15)

def iniciar_votacao():
    global votacao_ativa
    if not candidatos:
        messagebox.showwarning("Erro", "Nenhum candidato cadastrado.")
        return
    votacao_ativa = True
    registrar_voto()

def registrar_voto():
    if not votacao_ativa:
        return

    janela_votacao = tk.Toplevel(janela)
    janela_votacao.title("Votação")
    janela_votacao.geometry("400x450")

    tk.Label(janela_votacao, text="Digite sua matrícula:").pack(pady=5)
    entrada_matricula = tk.Entry(janela_votacao)
    entrada_matricula.pack(pady=5)

    tk.Label(janela_votacao, text="Digite o número do candidato:").pack(pady=5)
    entrada_voto = tk.Entry(janela_votacao)
    entrada_voto.pack(pady=5)

    label_imagem = tk.Label(janela_votacao)
    label_imagem.pack(pady=10)

    def confirmar_voto():
        matricula = entrada_matricula.get().strip()
        voto = entrada_voto.get().strip()

        if not matricula:
            messagebox.showwarning("Erro", "Matrícula não pode ser vazia.")
            return

        if matricula in matriculas_votantes:
            messagebox.showerror("Erro", "Esta matrícula já votou.")
            return

        candidato = next((c for c in candidatos if c["numero"] == voto), None)

        if candidato:
            caminho_foto = os.path.join(CAMINHO_IMG, candidato["foto"])
            try:
                imagem = Image.open(caminho_foto)
                imagem = imagem.resize((100, 100))
                foto_tk = ImageTk.PhotoImage(imagem)
                label_imagem.configure(image=foto_tk)
                label_imagem.image = foto_tk
            except Exception as e:
                label_imagem.configure(text="Erro ao carregar imagem.")
                print(e)
                return

            confirmar = messagebox.askyesno(
                "Confirmação",
                f"Confirmar voto para {candidato['nome']} ({candidato['partido']})?"
            )
            if confirmar:
                candidato["votos"] += 1
                matriculas_votantes.add(matricula)
                messagebox.showinfo("Sucesso", "Voto registrado com sucesso!")
                janela_votacao.destroy()
                registrar_voto()
        else:
            confirmar = messagebox.askyesno("Confirmação", "Candidato inexistente. Confirmar voto nulo?")
            if confirmar:
                matriculas_votantes.add(matricula)
                messagebox.showinfo("Sucesso", "Voto nulo registrado!")
                janela_votacao.destroy()
                registrar_voto()

    tk.Button(janela_votacao, text="Votar", command=confirmar_voto).pack(pady=10)

def imprime_relatorio():
    janela_relatorio = tk.Toplevel(janela)
    janela_relatorio.title("Resultados")
    janela_relatorio.geometry("400x300")

    total_votos = sum(c["votos"] for c in candidatos)
    linhas_relatorio = []

    if total_votos > 0:
        for candidato in candidatos:
            texto = f"{candidato['nome']} ({candidato['partido']}): {candidato['votos']} votos"
            linhas_relatorio.append(texto)
            tk.Label(janela_relatorio, text=texto).pack(pady=5)

        max_votos = max(c["votos"] for c in candidatos)
        vencedores = [c for c in candidatos if c["votos"] == max_votos]

        if len(vencedores) == 1:
            vencedor_texto = f"Vencedor: {vencedores[0]['nome']}"
        else:
            vencedor_texto = f"Empate entre: {', '.join(c['nome'] for c in vencedores)}"

        linhas_relatorio.append("")
        linhas_relatorio.append(vencedor_texto)
        tk.Label(janela_relatorio, text=vencedor_texto, font=("Arial", 12, "bold")).pack(pady=10)
    else:
        texto = "Não houve votos válidos."
        linhas_relatorio.append(texto)
        tk.Label(janela_relatorio, text=texto).pack(pady=10)

    try:
        nome_arquivo = "resultado_eleicao.pdf"
        c = canvas.Canvas(nome_arquivo, pagesize=A4)
        largura, altura = A4

        y = altura - 50
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, "RESULTADO DA ELEIÇÃO")
        y -= 30

        c.setFont("Helvetica", 12)
        c.drawString(50, y, f"Data e Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        y -= 30

        # Texto com resultados
        for linha in linhas_relatorio:
            c.drawString(50, y, linha)
            y -= 20

        # Foto do vencedor (se houver apenas um)
        if total_votos > 0 and len(vencedores) == 1:
            vencedor = vencedores[0]
            caminho_imagem = os.path.join(CAMINHO_IMG, vencedor["foto"])
            if os.path.exists(caminho_imagem):
                try:
                    largura_img = 150
                    altura_img = 150
                    x_img = (largura - largura_img) / 2
                    y -= altura_img + 10
                    c.drawImage(caminho_imagem, x_img, y, width=largura_img, height=altura_img)
                    y -= 30
                    c.setFont("Helvetica-Bold", 12)
                    c.drawCentredString(largura / 2, y, f"Foto do Vencedor: {vencedor['nome']}")
                except Exception as erro_img:
                    print("Erro ao adicionar imagem do vencedor:", erro_img)

        c.save()
        print(f"Relatório salvo como {nome_arquivo}")
        messagebox.showinfo("PDF gerado", f"Relatório salvo como '{nome_arquivo}'")

    except Exception as e:
        print("Erro ao gerar PDF:", e)
        messagebox.showerror("Erro", "Falha ao gerar o PDF.")

    tk.Button(janela_relatorio, text="Fechar", command=janela_relatorio.destroy).pack(pady=10)

def encerrar_votacao():
    global votacao_ativa
    votacao_ativa = False
    imprime_relatorio()

# Janela principal
janela = tk.Tk()
janela.title("Sistema de Votação")
mostrar_menu()
janela.mainloop()

