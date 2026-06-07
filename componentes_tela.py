import customtkinter as ctk
from tkinter import messagebox
from banco_dados import *
# Bibliotecas para a renderização do gráfico e efeitos visuais
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.patheffects as path_effects

class CardColapsavel(ctk.CTkFrame):
    def __init__(self, master, titulo, **kwargs):
        super().__init__(master, corner_radius=12, fg_color="#1e1e1e", border_width=1, border_color="#2d2d2d", **kwargs)
        self.expandido = True
        
        self.header = ctk.CTkFrame(self, fg_color="transparent", height=40)
        self.header.pack(fill="x", padx=12, pady=6)
        self.header.pack_propagate(False)
        
        self.lbl_titulo = ctk.CTkLabel(self.header, text=titulo, font=("Segoe UI", 11, "bold"), text_color="#a0aec0")
        self.lbl_titulo.pack(side="left")
        
        self.btn_min = ctk.CTkButton(self.header, text="—", width=28, height=22, 
                                     fg_color="#2d2d2d", hover_color="#ff4d88", 
                                     text_color="#ffffff", font=("Segoe UI", 12, "bold"),
                                     command=self.alternar)
        self.btn_min.pack(side="right")
        
        self.conteudo = ctk.CTkFrame(self, fg_color="transparent")
        self.conteudo.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    def alternar(self):
        if self.expandido:
            self.conteudo.pack_forget()
            self.btn_min.configure(text="+", fg_color="#ff4d88")
            self.expandido = False
        else:
            self.conteudo.pack(fill="both", expand=True, padx=12, pady=(0, 12))
            self.btn_min.configure(text="—", fg_color="#2d2d2d")
            self.expandido = True


class JanelaCadastro(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Criar Nova Conta")
        self.geometry("360x400")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.configure(fg_color="#0f0f0f")

        self.card = ctk.CTkFrame(self, corner_radius=12, fg_color="#1e1e1e")
        self.card.pack(padx=20, pady=20, fill="both", expand=True)

        ctk.CTkLabel(self.card, text="📝 REGISTRAR USUÁRIO", font=("Segoe UI", 16, "bold"), text_color="#ff4d88").pack(pady=20)

        self.ent_novo_user = ctk.CTkEntry(self.card, placeholder_text="Defina o Usuário", width=240, height=38, fg_color="#101010")
        self.ent_novo_user.pack(pady=8)

        self.ent_nova_senha = ctk.CTkEntry(self.card, placeholder_text="Defina a Senha", show="*", width=240, height=38, fg_color="#101010")
        self.ent_nova_senha.pack(pady=8)

        self.ent_confirma_senha = ctk.CTkEntry(self.card, placeholder_text="Confirme a Senha", show="*", width=240, height=38, fg_color="#101010")
        self.ent_confirma_senha.pack(pady=8)

        ctk.CTkButton(self.card, text="Salvar Cadastro", font=("Segoe UI", 12, "bold"), fg_color="#228B22", hover_color="#1a6b1a", width=240, height=40, command=self.executar_cadastro).pack(pady=25)

    def executar_cadastro(self):
        user = self.ent_novo_user.get().strip()
        senha = self.ent_nova_senha.get()
        confirma = self.ent_confirma_senha.get()

        if not user or not senha:
            messagebox.showerror("Erro", "Todos os campos devem ser preenchidos.")
            return

        if senha != confirma:
            messagebox.showerror("Erro", "As senhas não coincidem.")
            return

        sucesso = cadastrar_usuario(user, senha)
        if sucesso:
            messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso! Já pode fazer login.")
            self.destroy()
        else:
            messagebox.showerror("Erro", "Este nome de usuário já está em uso.")


class JanelaLogin(ctk.CTk):
    def __init__(self, callback_sucesso):
        super().__init__()
        self.callback_sucesso = callback_sucesso
        self.title("Acesso ao Sistema")
        self.geometry("400x480")
        self.resizable(False, False)

        self.card = ctk.CTkFrame(self, corner_radius=15, fg_color="#1e1e1e")
        self.card.pack(padx=30, pady=30, fill="both", expand=True)

        ctk.CTkLabel(self.card, text="FlexSpendeR", font=("Segoe UI", 22, "bold"), text_color="#ff4d88").pack(pady=(35, 15))

        self.ent_user = ctk.CTkEntry(self.card, placeholder_text="Usuário", width=250, height=40, fg_color="#101010")
        self.ent_user.pack(pady=10)
        
        self.ent_pass = ctk.CTkEntry(self.card, placeholder_text="Senha", show="*", width=250, height=40, fg_color="#101010")
        self.ent_pass.pack(pady=10)

        self.btn_login = ctk.CTkButton(self.card, text="Entrar", command=self.tentar_acesso, width=250, height=45, font=("Segoe UI", 14, "bold"), fg_color="#ff4d88", hover_color="#d43f72")
        self.btn_login.pack(pady=(25, 10))

        self.btn_ir_cadastro = ctk.CTkButton(self.card, text="Não tem conta? Cadastre-se aqui", fg_color="transparent", text_color="#a0aec0", hover_color="#1a1a1a", width=250, height=25, font=("Segoe UI", 11, "underline"), command=self.abrir_tela_cadastro)
        self.btn_ir_cadastro.pack(pady=5)

    def tentar_acesso(self):
        user_id = obter_id_autenticado(self.ent_user.get(), self.ent_pass.get())
        if user_id is not None:
            self.withdraw()  
            self.callback_sucesso(user_id)
        else:
            messagebox.showerror("Erro de Acesso", "Usuário ou senha incorretos.")

    def abrir_tela_cadastro(self):
        JanelaCadastro(self)


class JanelaPrincipal(ctk.CTk):
    def __init__(self, usuario_logado_id):
        super().__init__()
        self.usuario_logado_id = usuario_logado_id
        
        self.nome_usuario_ativo = obter_nome_usuario(self.usuario_logado_id)
        
        self.title("FlexSpendeR")
        self.geometry("800x600")
        self.resizable(False, False)
        self.configure(fg_color="#0f0f0f") 
        
        self.grid_columnconfigure(0, weight=4)
        self.grid_columnconfigure(1, weight=5)
        self.grid_rowconfigure(0, weight=1)

        # --- COLUNA ESQUERDA (PAINEL DE CONTROLE COM ROLAGEM) ---
        self.frame_esq = ctk.CTkScrollableFrame(self, fg_color="transparent", label_text="Painel de Controle", label_text_color="#718096")
        self.frame_esq.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")

        self.card_usuario = ctk.CTkFrame(self.frame_esq, corner_radius=12, fg_color="#2d2d2d", height=45)
        self.card_usuario.pack(fill="x", pady=(0, 10))
        self.card_usuario.pack_propagate(False)
        
        self.lbl_identificacao = ctk.CTkLabel(
            self.card_usuario, 
            text=f"👤 Sessão Ativa: {self.nome_usuario_ativo.upper()}", 
            font=("Segoe UI", 12, "bold"), 
            text_color="#ff4d88"
        )
        self.lbl_identificacao.pack(side="left", padx=15, fill="y")

        # [POSIÇÃO 1] Card Saldo Atualizado
        self.card_saldo = CardColapsavel(self.frame_esq, "FUNDO DISPONÍVEL EM CONTA")
        self.card_saldo.pack(fill="x", pady=(0, 10))
        
        self.lbl_saldo_valor = ctk.CTkLabel(self.card_saldo.conteudo, text="R$ 0,00", font=("Segoe UI", 28, "bold"), text_color="#ffffff")
        self.lbl_saldo_valor.pack(pady=5)
        
        self.barra = ctk.CTkProgressBar(self.card_saldo.conteudo, width=260, height=10, fg_color="#2d2d2d", progress_color="#228B22")
        self.barra.pack(pady=10)
        
        self.lbl_info = ctk.CTkLabel(self.card_saldo.conteudo, text="", font=("Segoe UI", 11, "italic"), text_color="#718096")
        self.lbl_info.pack(pady=(0, 5))
        
        self.ent_adicionar_fundo = ctk.CTkEntry(self.card_saldo.conteudo, placeholder_text="Adicionar valor à conta (R$)", height=32, fg_color="#101010")
        self.ent_adicionar_fundo.pack(fill="x", pady=4)
        
        self.btn_fundo = ctk.CTkButton(self.card_saldo.conteudo, text="Adicionar Fundos", font=("Segoe UI", 11, "bold"), fg_color="#ff4d88", hover_color="#d43f72", command=self.depositar_fundos)
        self.btn_fundo.pack(fill="x", pady=2)

        # [POSIÇÃO 2] Card Registrar Nova Despesa
        self.card_form = CardColapsavel(self.frame_esq, "REGISTRAR NOVA DESPESA")
        self.card_form.pack(fill="x", pady=(0, 10))
        
        self.ent_desc = ctk.CTkEntry(self.card_form.conteudo, placeholder_text="Descrição do Gasto", height=36, fg_color="#101010")
        self.ent_desc.pack(fill="x", pady=5)
        self.ent_val = ctk.CTkEntry(self.card_form.conteudo, placeholder_text="Valor (R$)", height=36, fg_color="#101010")
        self.ent_val.pack(fill="x", pady=5)
        
        self.cb_cat = ctk.CTkComboBox(self.card_form.conteudo, values=["Alimentação", "Lazer", "Transporte"], height=36, fg_color="#101010")
        self.cb_cat.pack(fill="x", pady=5)
        ctk.CTkButton(self.card_form.conteudo, text="Adicionar ao Histórico", font=("Segoe UI", 12, "bold"), fg_color="#ff4d88", hover_color="#d43f72", command=self.salvar_gasto).pack(fill="x", pady=10)

        # [POSIÇÃO 3] Card Dinâmico Cartão de Crédito
        self.card_cartao = CardColapsavel(self.frame_esq, "💳 CARTÕES DE CRÉDITO")
        self.card_cartao.pack(fill="x", pady=(0, 10))
        
        self.lbl_valor_fatura = ctk.CTkLabel(self.card_cartao.conteudo, text="Faturas Somadas: R$ 0,00", font=("Segoe UI", 16, "bold"), text_color="#ff4d88", anchor="w")
        self.lbl_valor_fatura.pack(fill="x", pady=(2, 8))

        self.scroll_cartoes = ctk.CTkScrollableFrame(self.card_cartao.conteudo, fg_color="#101010", height=105, corner_radius=6)
        self.scroll_cartoes.pack(fill="x", pady=5)

        self.ent_nome_banco = ctk.CTkEntry(self.card_cartao.conteudo, placeholder_text="Nome do Banco (Ex: Nubank)", height=32, fg_color="#101010")
        self.ent_nome_banco.pack(fill="x", pady=4)
        
        container_grid_cartao = ctk.CTkFrame(self.card_cartao.conteudo, fg_color="transparent")
        container_grid_cartao.pack(fill="x", pady=2)
        container_grid_cartao.grid_columnconfigure(0, weight=1)
        container_grid_cartao.grid_columnconfigure(1, weight=1)

        self.ent_fatura_banco = ctk.CTkEntry(container_grid_cartao, placeholder_text="Fatura (R$)", height=32, fg_color="#101010")
        self.ent_fatura_banco.grid(row=0, column=0, padx=(0, 4), sticky="ew")
        
        self.ent_vencimento_banco = ctk.CTkEntry(container_grid_cartao, placeholder_text="Dia Venc. (1 a 31)", height=32, fg_color="#101010")
        self.ent_vencimento_banco.grid(row=0, column=1, padx=(4, 0), sticky="ew")

        self.btn_salvar_cartao = ctk.CTkButton(self.card_cartao.conteudo, text="Adicionar Novo Cartão", height=34, font=("Segoe UI", 11, "bold"), fg_color="#2d2d2d", hover_color="#404040", command=self.cadastrar_novo_cartao)
        self.btn_salvar_cartao.pack(fill="x", pady=(6, 2))

        self.btn_reset_total = ctk.CTkButton(
            self.frame_esq, 
            text="⚠️ Reiniciar Conta do Zero", 
            font=("Segoe UI", 11, "bold"), 
            fg_color="#8b0000", 
            hover_color="#5a0000", 
            height=35,
            command=self.executar_redefinicao_total
        )
        self.btn_reset_total.pack(fill="x", pady=(10, 5))


        # --- COLUNA DIREITA (HISTÓRICO) ---
        self.card_dir = ctk.CTkFrame(self, corner_radius=12, fg_color="#1e1e1e", border_width=1, border_color="#2d2d2d")
        self.card_dir.grid(row=0, column=1, padx=(0, 15), pady=15, sticky="nsew")
        
        header_dir = ctk.CTkFrame(self.card_dir, fg_color="transparent")
        header_dir.pack(fill="x", padx=15, pady=15)
        ctk.CTkLabel(header_dir, text="Histórico Financeiro", font=("Segoe UI", 15, "bold"), text_color="#ffffff").pack(side="left")
        
        self.filtro = ctk.CTkComboBox(header_dir, values=["Todos", "Alimentação", "Lazer", "Transporte"], command=lambda e: self.atualizar_lista(), width=130, fg_color="#101010")
        self.filtro.set("Todos")
        self.filtro.pack(side="right")
        
        # BOTÃO PARA ABRIR O GRÁFICO
        self.btn_grafico = ctk.CTkButton(header_dir, text="📊 Ver Gráfico", width=100, font=("Segoe UI", 11, "bold"), fg_color="#2d2d2d", hover_color="#404040", command=self.abrir_grafico_pizza)
        self.btn_grafico.pack(side="right", padx=10)

        self.scroll = ctk.CTkScrollableFrame(self.card_dir, fg_color="#0f0f0f", corner_radius=8)
        self.scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self.atualizar_visual()

    def abrir_grafico_pizza(self):
        dados_categorias = obter_gastos_por_categoria(self.usuario_logado_id)
        
        if not dados_categorias:
            messagebox.showinfo("Sem dados", "Você ainda não possui despesas registradas para gerar o gráfico.")
            return

        categorias = [linha[0] for linha in dados_categorias]
        valores = [linha[1] for linha in dados_categorias]

        # Configurando a janela flutuante
        janela_grafico = ctk.CTkToplevel(self)
        janela_grafico.title("Análise de Gastos por Categoria")
        janela_grafico.geometry("500x450")
        janela_grafico.attributes("-topmost", True)
        janela_grafico.configure(fg_color="#1e1e1e")

        # Criando a figura do Matplotlib com design escuro
        fig, ax = plt.subplots(figsize=(5, 4), facecolor="#1e1e1e")
        
        # Lista de cores atualizada (incluindo uma cor para "Faturas")
        cores_personalizadas = ["#ff4d88", "#228B22", "#ecc94b", "#4299e1", "#9f7aea", "#ffcc00"]
        
        # Criação do gráfico
        patches, texts, autotexts = ax.pie(
            valores, 
            labels=categorias, 
            autopct='%1.1f%%', 
            startangle=140, 
            colors=cores_personalizadas,
            textprops={'fontweight': 'bold'}
        )

        # 1. Zoom ajustado e remoção dos eixos
        ax.set_xlim(-1.1, 1.1)
        ax.set_ylim(-1.1, 1.1)
        ax.axis('off')

        # 2. Aplicação de cores dinâmicas e contorno (outline) preto nos textos
        for text, autotext, patch in zip(texts, autotexts, patches):
            cor_da_fatia = patch.get_facecolor()
            
            # Pinta o texto da categoria
            text.set_color(cor_da_fatia)
            
            # Pinta a porcentagem
            autotext.set_color(cor_da_fatia)
            
            # Aplica o efeito de contorno preto de 2px
            autotext.set_path_effects([
                path_effects.Stroke(linewidth=2, foreground='black'),
                path_effects.Normal()
            ])

        ax.set_title("Percentual de Despesas", color="white", fontweight="bold", pad=20)
        
        # Embutindo o gráfico no CustomTkinter
        canvas = FigureCanvasTkAgg(fig, master=janela_grafico)
        canvas.draw()
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill="both", expand=True, padx=10, pady=10)

    def executar_redefinicao_total(self):
        pergunta = messagebox.askyesno(
            "Confirmação de Redefinição", 
            f"Atenção {self.nome_usuario_ativo.upper()},\n\n"
            "Esta ação irá apagar definitivamente o seu saldo base, "
            "todo o seu histórico de gastos e seus cartões de crédito.\n\n"
            "O seu perfil de acesso continuará ativo. Deseja prosseguir?"
        )
        if pergunta:
            reiniciar_dados_usuario(self.usuario_logado_id)
            self.atualizar_visual()
            messagebox.showinfo("Dados Reiniciados", "Todos os seus dados financeiros foram limpos com sucesso!")

    def depositar_fundos(self):
        valor_str = self.ent_adicionar_fundo.get()
        if not valor_str: return
        try:
            v = float(valor_str.replace(',', '.'))
            if v <= 0: raise ValueError
            adicionar_fundos_banco(self.usuario_logado_id, v)
            self.ent_adicionar_fundo.delete(0, 'end')
            self.atualizar_visual()
            messagebox.showinfo("Sucesso", f"R$ {v:.2f} adicionados à conta!")
        except ValueError:
            messagebox.showerror("Erro", "Insira um valor numérico válido.")

    def cadastrar_novo_cartao(self):
        banco_digitado = self.ent_nome_banco.get().strip()
        valor_digitado = self.ent_fatura_banco.get().strip()
        vencimento_digitado = self.ent_vencimento_banco.get().strip()
        
        if not banco_digitado or not valor_digitado or not vencimento_digitado:
            messagebox.showerror("Erro", "Preencha todos os campos do cartão (Banco, Valor e Vencimento).")
            return
            
        try:
            dia_vencimento = int(vencimento_digitado)
            if dia_vencimento < 1 or dia_vencimento > 31:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Dia de Vencimento Inválido", 
                "O dia de vencimento deve ser apenas um número inteiro entre 1 e 31.\n\n"
                "Exemplo correto de preenchimento:\n"
                "• Se a fatura vence no dia dez, digite apenas: 10\n"
                "• Se vence no dia cinco, digite apenas: 5"
            )
            return

        try:
            v = float(valor_digitado.replace(',', '.'))
            if v < 0: raise ValueError
            inserir_cartao(self.usuario_logado_id, banco_digitado, v, str(dia_vencimento))
            self.ent_nome_banco.delete(0, 'end')
            self.ent_fatura_banco.delete(0, 'end')
            self.ent_vencimento_banco.delete(0, 'end')
            self.atualizar_visual()
        except ValueError:
            messagebox.showerror("Erro", "Valor de fatura incorreto.")

    def remover_cartao_fluxo(self, id_c):
        deletar_cartao(id_c)
        self.atualizar_visual()

    def pagar_fatura_fluxo(self, id_c):
        dados_cartao = obter_cartao_por_id(id_c)
        if dados_cartao:
            banco, valor_fatura = dados_cartao
            if messagebox.askyesno("Confirmar Pagamento", f"Confirmar pagamento da fatura do {banco}?"):
                # MUDANÇA: Alterado de "Lazer" para "Fatura" para aparecer como fatia própria no gráfico
                inserir_transacao(self.usuario_logado_id, f"Pagamento: {banco}", valor_fatura, "Fatura")
                deletar_cartao(id_c)
                self.atualizar_visual()

    def salvar_gasto(self):
        try:
            d = self.ent_desc.get()
            v = float(self.ent_val.get().replace(',', '.'))
            c = self.cb_cat.get()
            if not d or v <= 0: raise ValueError
            inserir_transacao(self.usuario_logado_id, d, v, c)
            self.ent_desc.delete(0, 'end')
            self.ent_val.delete(0, 'end')
            self.atualizar_visual()
        except:
            messagebox.showerror("Erro", "Verifique os dados da despesa.")

    def atualizar_lista_cartoes(self):
        for w in self.scroll_cartoes.winfo_children(): w.destroy()
        cartoes = obter_todos_cartoes(self.usuario_logado_id)
        
        if not cartoes:
            ctk.CTkLabel(self.scroll_cartoes, text="Nenhum cartão cadastrado.", font=("Segoe UI", 11, "italic"), text_color="#555").pack(pady=15)
            return

        for c in cartoes:
            f_row = ctk.CTkFrame(self.scroll_cartoes, fg_color="transparent", height=28)
            f_row.pack(fill="x", pady=2)
            f_row.pack_propagate(False)
            
            ctk.CTkButton(f_row, text="✕", width=18, height=18, fg_color="#e53e3e", hover_color="#c53030", font=("Segoe UI", 8, "bold"), command=lambda idx=c[2]: self.remover_cartao_fluxo(idx)).pack(side="left", padx=(5, 4))
            ctk.CTkButton(f_row, text="✓", width=18, height=18, fg_color="#228B22", hover_color="#1a6b1a", font=("Segoe UI", 9, "bold"), command=lambda idx=c[2]: self.pagar_fatura_fluxo(idx)).pack(side="left", padx=(0, 8))
            ctk.CTkLabel(f_row, text=f"{c[0]} (Dia: {c[3]})", font=("Segoe UI", 12), text_color="#ffffff", anchor="w").pack(side="left", fill="both", expand=True)
            ctk.CTkLabel(f_row, text=f"R$ {c[1]:.2f}", font=("Segoe UI", 11, "bold"), text_color="#ffffff").pack(side="right", padx=5)

    def atualizar_lista(self):
        for w in self.scroll.winfo_children(): w.destroy()
        gastos = obter_gastos_filtrados(self.usuario_logado_id, self.filtro.get())
        
        if not gastos:
            ctk.CTkLabel(self.scroll, text="Nenhum gasto registrado.", font=("Segoe UI", 12, "italic"), text_color="#718096").pack(pady=30)
            return

        for g in gastos:
            f = ctk.CTkFrame(self.scroll, fg_color="#1e1e1e", height=45, corner_radius=6, border_width=1, border_color="#2d2d2d")
            f.pack(fill="x", pady=3, padx=5)
            f.pack_propagate(False)
            
            ctk.CTkButton(f, text="✕", width=24, height=24, fg_color="#e53e3e", hover_color="#c53030", font=("Segoe UI", 10, "bold"), command=lambda i=g[3]: self.deletar(i)).pack(side="left", padx=10)
            ctk.CTkLabel(f, text=f"{g[0]}", font=("Segoe UI", 12, "bold"), text_color="#ffffff", anchor="w").pack(side="left", fill="both", expand=True)
            ctk.CTkLabel(f, text=f"[{g[2]}] ", font=("Segoe UI", 11, "italic"), text_color="#718096").pack(side="left")
            ctk.CTkLabel(f, text=f"R$ {g[1]:.2f} ", font=("Segoe UI", 12, "bold"), text_color="#ff4d88").pack(side="right", padx=10)

    def deletar(self, id_g):
        if messagebox.askyesno("Excluir", "Deseja apagar este registro?"):
            deletar_transacao(id_g)
            self.atualizar_visual()

    def atualizar_visual(self):
        saldo_bruto = carregar_saldo_base(self.usuario_logado_id)
        gasto_total = obter_total_gastos(self.usuario_logado_id)
        saldo_real = saldo_bruto - gasto_total
        
        self.lbl_saldo_valor.configure(text=f"R$ {saldo_real:.2f}")
        self.lbl_info.configure(text=f"Total Depositado: R$ {saldo_bruto:.2f} | Gastos: R$ {gasto_total:.2f}")
        
        if saldo_real < 0:
            porcentagem = 1.0
            cor_barra = "#e53e3e"
        elif saldo_bruto == 0:
            porcentagem = 0.0
            cor_barra = "#228B22"
        else:
            porcentagem = max(saldo_real / saldo_bruto, 0.0)
            if porcentagem > 0.5:
                cor_barra = "#228B22"
            elif porcentagem > 0.15:
                cor_barra = "#ecc94b"
            else:
                cor_barra = "#e53e3e"
            
        self.barra.set(porcentagem)
        self.barra.configure(progress_color=cor_barra)
        
        faturas_somadas = obter_total_faturas(self.usuario_logado_id)
        self.lbl_valor_fatura.configure(text=f"Faturas Somadas: R$ {faturas_somadas:.2f}")
        
        self.atualizar_lista_cartoes()
        self.atualizar_lista()