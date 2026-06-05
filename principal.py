import datetime
import tkinter as tk
from tkinter import messagebox, simpledialog
import customtkinter as ctk

# Configuração visual do CustomTkinter
ctk.set_appearance_mode("System")  # Segue o modo do sistema (Dark/Light)
ctk.set_default_color_theme("blue")

# ==========================================
# CLASSES DE NEGÓCIO (MODELOS)
# ==========================================

class Investimento:
    """Classe responsável por gerenciar os investimentos de um jogador."""
    def __init__(self):
        self.renda_fixa_acumulado = 0.0

    def investir_renda_fixa(self, valor: float):
        self.renda_fixa_acumulado += valor

    def rodar_renda_fixa(self) -> float:
        """Aplica 5% de rendimento sobre o valor acumulado em Renda Fixa."""
        rendimento = self.renda_fixa_acumulado * 0.05
        self.renda_fixa_acumulado += rendimento
        return rendimento


class Jogador:
    """Classe que representa um jogador e encapsula suas regras financeiras."""
    def __init__(self, id_jog: int, nome: str, salario: float, patrimonio_inicial: float, membros_familia: int):
        self.id = id_jog
        self.nome = nome
        self.salario = salario
        self.patrimonio_inicial = patrimonio_inicial
        self.patrimonio_atual = patrimonio_inicial
        self.membros_familia = membros_familia
        
        # Sistemas acoplados
        self.investimento = Investimento()
        self.parcelas_carro = []  # Lista de valores de parcelas pendentes
        
    @property
    def variacao_patrimonio(self) -> float:
        """Calcula a variação percentual do patrimônio."""
        if self.patrimonio_inicial == 0:
            return 0.0
        return ((self.patrimonio_atual - self.patrimonio_inicial) / self.patrimonio_inicial) * 100

    def clonar_estado(self):
        """Retorna um dicionário com a cópia do estado atual (para o sistema de Desfazer)."""
        return {
            "salario": self.salario,
            "patrimonio_atual": self.patrimonio_atual,
            "membros_familia": self.membros_familia,
            "renda_fixa": self.investimento.renda_fixa_acumulado,
            "parcelas_carro": list(self.parcelas_carro)
        }

    def restaurar_estado(self, estado: dict):
        """Restaura o estado do jogador a partir de um snapshot."""
        self.salario = estado["salario"]
        self.patrimonio_atual = estado["patrimonio_atual"]
        self.membros_familia = estado["membros_familia"]
        self.investimento.renda_fixa_acumulado = estado["renda_fixa"]
        self.parcelas_carro = list(estado["parcelas_carro"])


class SistemaJogo:
    """Gerenciador central dos estados dos jogadores e histórico da partida."""
    def __init__(self):
        self.jogadores = []
        self.historico = []
        self.historico_estados = []  # Pilha para o comando Desfazer (Ctrl+Z)
        self.inicializar_jogadores_padrao()

    def inicializar_jogadores_padrao(self):
        """Cria 6 jogadores padrão para iniciar o tabuleiro."""
        nomes_padrao = ["Ana", "Bruno", "Carlos", "Diana", "Eduardo", "Fernanda"]
        for i, nome in enumerate(nomes_padrao):
            # ID, Nome, Salário base, Patrimônio Inicial, Membros da família
            j = Jogador(i + 1, nome, 3000.0 + (i * 500), 5000.0 + (i * 1000), 2 + (i % 3))
            self.jogadores.append(j)

    def salvar_estado_atual(self):
        """Salva o estado de todos os jogadores antes de qualquer alteração."""
        snapshot = {j.id: j.clonar_estado() for j in self.jogadores}
        self.historico_estados.append(snapshot)
        if len(self.historico_estados) > 20:  # Limita o histórico de undo a 20 ações
            self.historico_estados.pop(0)

    def desfazer_ultima_acao(self) -> bool:
        """Retorna os jogadores ao estado anterior à última alteração."""
        if not self.historico_estados:
            return False
        ultimo_estado = self.historico_estados.pop()
        for j in self.jogadores:
            if j.id in ultimo_estado:
                j.restaurar_estado(ultimo_estado[j.id])
        self.registrar_log("Sistema", "Ação Desfeita", 0, "Retorno ao estado anterior")
        return True

    def registrar_log(self, jogador_nome: str, casa_ou_acao: str, valor: float, detalhe: str = ""):
        """Adiciona um registro ao histórico do jogo com timestamp."""
        agora = datetime.datetime.now().strftime("%H:%M:%S")
        sinal = "+" if valor > 0 else ""
        val_str = f" ({sinal}R${valor:.2f})" if valor != 0 else ""
        msg = f"[{agora}] {jogador_nome} -> {casa_ou_acao}{val_str}. {detalhe}"
        self.historico.insert(0, msg)

    def obter_lider(self) -> Jogador:
        """Retorna o jogador que está vencendo (maior variação patrimonial)."""
        if not self.jogadores:
            return None
        return max(self.jogadores, key=lambda j: j.variacao_patrimonio)


# ==========================================
# INTERFACE GRÁFICA (VIEW / CONTROLLER)
# ==========================================

class AppFinanceiro(ctk.CTk):
    def __init__(self, sistema: SistemaJogo):
        super().__init__()
        self.sistema = sistema
        
        self.title("Gerenciador de Tabuleiro - Educação Financeira")
        self.geometry("1280 cavalos", "750")
        self.minsize(1100, 700)

        self.jogador_selecionado_id = tk.IntVar(value=1)

        self.criar_layout()
        self.atualizar_tela()

    def criar_layout(self):
        # Grid Principal do App (2 Colunas: Esquerda = Dados/Ações, Direita = Logs/Ranking)
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        # ---------------- COLUNA ESQUERDA ----------------
        frame_esquerda = ctk.CTkFrame(self)
        frame_esquerda.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        frame_esquerda.grid_columnconfigure(0, weight=1)
        frame_esquerda.grid_rowconfigure(0, weight=4)  # Painel de Jogadores
        frame_esquerda.grid_rowconfigure(1, weight=3)  # Botões de Ações

        # Painel dos Jogadores
        self.frame_jogadores = ctk.CTkScrollableFrame(frame_esquerda, label_text="STATUS DOS JOGADORES")
        self.frame_jogadores.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Abas de Ações (Casas do Tabuleiro / Modificadores Manuais)
        self.abas_acoes = ctk.CTkTabview(frame_esquerda)
        self.abas_acoes.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.tab_casas = self.abas_acoes.add("Casas do Tabuleiro")
        self.tab_ajustes = self.abas_acoes.add("Ajustes Manuais")
        
        self.configurar_botoes_casas()
        self.configurar_botoes_ajustes()

        # ---------------- COLUNA DIREITA ----------------
        frame_direita = ctk.CTkFrame(self)
        frame_direita.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")
        frame_direita.grid_columnconfigure(0, weight=1)
        frame_direita.grid_rowconfigure(0, weight=2)  # Ranking
        frame_direita.grid_rowconfigure(1, weight=3)  # Histórico

        # Ranking
        self.frame_ranking = ctk.CTkFrame(frame_direita)
        self.frame_ranking.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.label_ranking_titulo = ctk.CTkLabel(self.frame_ranking, text="🏆 RANKING ATUAL", font=ctk.CTkFont(size=16, weight="bold"))
        self.label_ranking_titulo.pack(pady=5)
        self.txt_ranking = ctk.CTkTextbox(self.frame_ranking, font=ctk.CTkFont(size=13))
        self.txt_ranking.pack(fill="both", expand=True, padx=10, pady=5)

        # Histórico de Logs
        frame_historico = ctk.CTkFrame(frame_direita)
        frame_historico.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        label_hist_titulo = ctk.CTkLabel(frame_historico, text="📋 HISTÓRICO DE EVENTOS", font=ctk.CTkFont(size=14, weight="bold"))
        label_hist_titulo.pack(pady=5)
        self.txt_historico = ctk.CTkTextbox(frame_historico, font=ctk.CTkFont(size=12))
        self.txt_historico.pack(fill="both", expand=True, padx=10, pady=5)

    def configurar_botoes_casas(self):
        """Cria e organiza os botões para aplicar o efeito de cada casa."""
        # Usando Grid para organizar os botões das Casas de forma limpa
        for i in range(4): self.tab_casas.grid_columnconfigure(i, weight=1)
        
        botoes = [
            ("C1: Juros 3000%", lambda: self.executar_casa_juros(), 0, 0),
            ("C2: Comprar Carro", lambda: self.executar_casa_carro(), 0, 1),
            ("C3: Pagar Aluguel", lambda: self.executar_casa_aluguel(), 0, 2),
            ("C4: Compra do Mês", lambda: self.executar_casa_compra_mes(), 0, 3),
            
            ("C5: Pagar Luz", lambda: self.executar_casa_luz(), 1, 0),
            ("C6: Pagar Água", lambda: self.executar_casa_agua(), 1, 1),
            ("C7: Tigrinho 🐯", lambda: self.executar_casa_tigrinho(), 1, 2),
            ("C8: Inv. Renda Fixa", lambda: self.executar_casa_investimento_fixo(), 1, 3),
            
            ("C8: Inv. Variável", lambda: self.executar_casa_investimento_variavel(), 2, 0),
            ("C8: Render Fixa (5%)", lambda: self.executar_render_fixa_geral(), 2, 1),
            ("C9: Promoção (+25%)", lambda: self.executar_casa_promocao(), 2, 2),
            ("C10: Redução (-10%)", lambda: self.executar_casa_reducao(), 2, 3),
            
            ("C11: Hospital (-R$300)", lambda: self.executar_casa_hospital(), 3, 0)
        ]

        for texto, comando, linha, col in botoes:
            btn = ctk.CTkButton(self.tab_casas, text=texto, command=comando, font=ctk.CTkFont(size=12))
            btn.grid(row=linha, column=col, padx=5, pady=8, sticky="nsew")

    def configurar_botoes_ajustes(self):
        """Cria botões de correção manual de valores."""
        for i in range(3): self.tab_ajustes.grid_columnconfigure(i, weight=1)

        ctk.CTkButton(self.tab_ajustes, text="➕ Adicionar ao Patrimônio", fg_color="#27ae60", hover_color="#218c53",
                      command=lambda: self.ajuste_patrimonio(dinheiro=True)).grid(row=0, column=0, padx=5, pady=10, sticky="wse" if True else "nsew")
        ctk.CTkButton(self.tab_ajustes, text="➖ Retirar do Patrimônio", fg_color="#c0392b", hover_color="#962d22",
                      command=lambda: self.ajuste_patrimonio(dinheiro=False)).grid(row=0, column=1, padx=5, pady=10, sticky="nsew")
        ctk.CTkButton(self.tab_ajustes, text="⚙️ Alterar Salário", command=self.ajuste_salario_direto).grid(row=0, column=2, padx=5, pady=10, sticky="nsew")
        
        ctk.CTkButton(self.tab_ajustes, text="📝 Editar Todos os Dados", command=self.abrir_janela_edicao_jogador).grid(row=1, column=0, padx=5, pady=10, sticky="nsew")
        ctk.CTkButton(self.tab_ajustes, text="🔄 DESFAZER ÚLTIMA AÇÃO", fg_color="#d35400", hover_color="#a04000",
                      command=self.executar_desfazer).grid(row=1, column=1, columnspan=2, padx=5, pady=10, sticky="nsew")

    # ==========================================
    # ATUALIZAÇÃO E RENDERIZAÇÃO DA DA TELA
    # ==========================================

    def atualizar_tela(self):
        """Atualiza todos os componentes visuais baseando-se no estado atual do sistema."""
        # 1. Limpar e renderizar a lista de status de jogadores
        for widget in self.frame_jogadores.winfo_children():
            widget.destroy()

        lider = self.sistema.obtain_lider() if hasattr(self.sistema, "obtain_lider") else self.sistema.obter_lider()

        for j in self.sistema.jogadores:
            # Container de cada jogador
            eh_lider = (lider and lider.id == j.id)
            borda_cor = "#f1c40f" if eh_lider else "transparent"
            
            frame_j = ctk.CTkFrame(self.frame_jogadores, border_width=2 if eh_lider else 0, border_color=borda_cor)
            frame_j.pack(fill="x", padx=5, pady=5)

            # RadioButton para seleção do jogador ativo nas ações
            rb = ctk.CTkRadioButton(frame_j, text="", variable=self.jogador_selecionado_id, value=j.id)
            rb.pack(side="left", padx=10)

            # Textos informativos do Jogador
            lider_tag = " [👑 LÍDER]" if eh_lider else ""
            txt_nome = f"{j.nome}{lider_tag}\nFamília: {j.membros_familia} pessoas"
            lbl_nome = ctk.CTkLabel(frame_j, text=txt_nome, font=ctk.CTkFont(weight="bold"), justify="left")
            lbl_nome.pack(side="left", padx=10, pady=5)

            txt_financas = f"Salário: R${j.salario:.2f}  |  Patrimônio: R${j.patrimonio_atual:.2f}"
            lbl_financas = ctk.CTkLabel(frame_j, text=txt_financas, justify="left")
            lbl_financas.pack(side="left", padx=20)

            # Variação Percentual
            cor_var = "#2ecc71" if j.variacao_patrimonio >= 0 else "#e74c3c"
            lbl_var = ctk.CTkLabel(frame_j, text=f"{j.variacao_patrimonio:+.1f}%", text_color=cor_var, font=ctk.CTkFont(weight="bold"))
            lbl_var.pack(side="right", padx=20)

        # 2. Atualizar Ranking Comercial
        self.txt_ranking.configure(state="normal")
        self.txt_ranking.delete("1.0", "end")
        
        jogadores_ordenados = sorted(self.sistema.jogadores, key=lambda x: x.variacao_patrimonio, reverse=True)
        for rank, j in enumerate(jogadores_ordenados, 1):
            medalha = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"{rank}º"
            self.txt_ranking.insert("end", f"{medalha} {j.nome} | Var: {j.variacao_patrimonio:+.2f}% (Patr: R${j.patrimonio_atual:.2f})\n")
        
        if lider:
            self.txt_ranking.insert("end", f"\n VENCEDOR ATUAL CASO O JOGO ACABASSE: {lider.nome} 🎉")
        self.txt_ranking.configure(state="disabled")

        # 3. Atualizar Logs do Histórico
        self.txt_historico.configure(state="normal")
        self.txt_historico.delete("1.0", "end")
        for log in self.sistema.historico:
            self.txt_historico.insert("end", log + "\n")
        self.txt_historico.configure(state="disabled")

    def obter_jogador_selecionado(self) -> Jogador:
        id_sel = self.jogador_selecionado_id.get()
        return next(j for j in self.sistema.jogadores if j.id == id_sel)

    # ==========================================
    # LOGICA DAS CASAS DO TABULEIRO
    # ==========================================

    def executar_casa_juros(self):
        j = self.obter_jogador_selecionado()
        divida = simpledialog.askfloat("Casa 1 - Juros 3000%", f"Digite o valor da dívida de {j.nome}:", minvalue=0)
        if divida is None: return
        rodadas = simpledialog.askinteger("Casa 1", "Digite a quantidade de rodadas:", minvalue=1)
        if rodadas is None: return

        self.sistema.salvar_estado_atual()
        # Cálculo fictício/educativo expressivo baseado no enunciado de juros altíssimos
        taxa = 30.0  # 3000% transformado em fator multiplicador direto por rodada
        impacto = divida * (taxa * rodadas)
        j.patrimonio_atual -= impacto
        self.sistema.registrar_log(j.nome, "Casa 1: Juros 3000%", -impacto, f"Dívida de R${divida:.2f} por {rodadas} rodada(s)")
        self.atualizar_tela()

    def executar_casa_carro(self):
        j = self.obter_jogador_selecionado()
        valor_carro = j.salario * 4.5
        
        if not messagebox.askyesno("Casa 2 - Carro 450%", f"Deseja comprar um carro no valor de R${valor_carro:.2f} (450% do salário)?"):
            return

        parcelas = simpledialog.askinteger("Parcelamento", "Deseja parcelar em quantas vezes? (Até 30x):", minvalue=1, maxvalue=30)
        if not parcelas: return

        self.sistema.salvar_estado_atual()
        valor_parcela = valor_carro / parcelas
        j.patrimonio_atual -= valor_carro  # O patrimônio líquido cai pelo valor total ou registra-se a transação
        j.parcelas_carro.extend([valor_parcela] * parcelas)
        
        self.sistema.registrar_log(j.nome, "Casa 2: Comprou Carro", -valor_carro, f"Parcelado em {parcelas}x de R${valor_parcela:.2f}")
        self.atualizar_tela()

    def executar_casa_aluguel(self):
        j = self.obter_jogador_selecionado()
        self.sistema.salvar_estado_atual()
        custo = j.salario * 0.30
        j.patrimonio_atual -= custo
        self.sistema.registrar_log(j.nome, "Casa 3: Aluguel (30%)", -custo)
        self.atualizar_tela()

    def executar_casa_compra_mes(self):
        j = self.obter_jogador_selecionado()
        self.sistema.salvar_estado_atual()
        porcentagem = 0.05 * j.membros_familia
        custo = j.salario * porcentagem
        j.patrimonio_atual -= custo
        self.sistema.registrar_log(j.nome, f"Casa 4: Compra do Mês ({porcentagem*100:.0f}%)", -custo, f"{j.membros_familia} membros")
        self.atualizar_tela()

    def executar_casa_luz(self):
        j = self.obter_jogador_selecionado()
        self.sistema.salvar_estado_atual()
        porcentagem = 0.01 * j.membros_familia
        custo = j.salario * porcentagem
        j.patrimonio_atual -= custo
        self.sistema.registrar_log(j.nome, f"Casa 5: Conta de Luz ({porcentagem*100:.0f}%)", -custo)
        self.atualizar_tela()

    def executar_casa_agua(self):
        j = self.obter_jogador_selecionado()
        self.sistema.salvar_estado_atual()
        porcentagem = 0.01 * j.membros_familia
        custo = j.salario * porcentagem
        j.patrimonio_atual -= custo
        self.sistema.registrar_log(j.nome, f"Casa 6: Conta de Água ({porcentagem*100:.0f}%)", -custo)
        self.atualizar_tela()

    def executar_casa_tigrinho(self):
        j = self.obter_jogador_selecionado()
        valor = simpledialog.askfloat("Casa 7 - Sorte/Azar", "Digite o valor ganho (positivo) ou perdido (negativo):")
        if valor is None: return

        self.sistema.salvar_estado_atual()
        j.patrimonio_atual += valor
        acao = "Ganhou no Tigrinho" if valor >= 0 else "Perdeu no Tigrinho"
        self.sistema.registrar_log(j.nome, f"Casa 7: {acao}", valor)
        self.atualizar_tela()

    def executar_casa_investimento_fixo(self):
        j = self.obter_jogador_selecionado()
        valor = simpledialog.askfloat("Casa 8 - Renda Fixa", "Quanto deseja alocar em Renda Fixa?", minvalue=0)
        if valor is None: return

        if valor > j.patrimonio_atual:
            messagebox.showwarning("Saldo Insuficiente", "O jogador não possui patrimônio suficiente livre.")
            return

        self.sistema.salvar_estado_atual()
        j.patrimonio_atual -= valor
        j.investimento.investir_renda_fixa(valor)
        self.sistema.registrar_log(j.nome, "Casa 8: Aplicou Renda Fixa", -valor, f"Total Aplicado: R${j.investimento.renda_fixa_acumulado:.2f}")
        self.atualizar_tela()

    def executar_render_fixa_geral(self):
        """Aplica o rendimento de 5% da renda fixa para o jogador selecionado."""
        j = self.obter_jogador_selecionado()
        if j.investimento.renda_fixa_acumulado <= 0:
            messagebox.showinfo("Aviso", f"{j.nome} não possui ativos em Renda Fixa para render.")
            return

        self.sistema.salvar_estado_atual()
        rendimento = j.investimento.rodar_renda_fixa()
        j.patrimonio_atual += rendimento
        self.sistema.registrar_log(j.nome, "Rendimento Renda Fixa (+5%)", rendimento, f"Novo Saldo Investido: R${j.investimento.renda_fixa_acumulado:.2f}")
        self.atualizar_tela()

    def executar_casa_investimento_variavel(self):
        j = self.obter_jogador_selecionado()
        valor = simpledialog.askfloat("Casa 8 - Renda Variável", "Informe o Ganho (+) ou Perda (-) do mercado:")
        if valor is None: return

        self.sistema.salvar_estado_atual()
        j.patrimonio_atual += valor
        acao = "Renda Variável (Lucro)" if valor >= 0 else "Renda Variável (Prejuízo)"
        self.sistema.registrar_log(j.nome, f"Casa 8: {acao}", valor)
        self.atualizar_tela()

    def executar_casa_promocao(self):
        j = self.obter_jogador_selecionado()
        self.sistema.salvar_estado_atual()
        aumento = j.salario * 0.25
        j.salario += aumento
        self.sistema.registrar_log(j.nome, "Casa 9: Promoção no Trabalho", 0, f"Salário aumentado em 25% para R${j.salario:.2f}")
        self.atualizar_tela()

    def executar_casa_reducao(self):
        j = self.obter_jogador_selecionado()
        self.sistema.salvar_estado_atual()
        queda = j.salario * 0.10
        j.salario -= queda
        self.sistema.registrar_log(j.nome, "Casa 10: Redução Salarial", 0, f"Salário reduzido em 10% para R${j.salario:.2f}")
        self.atualizar_tela()

    def executar_casa_hospital(self):
        j = self.obter_jogador_selecionado()
        self.sistema.salvar_estado_atual()
        j.patrimonio_atual -= 300
        self.sistema.registrar_log(j.nome, "Casa 11: Despesa Hospitalar", -300)
        self.atualizar_tela()

    # ==========================================
    # CORREÇÕES MANUAIS E UTILITÁRIOS
    # ==========================================

    def ajuste_patrimonio(self, dinheiro: bool):
        j = self.obter_jogador_selecionado()
        acao_nome = "Adicionar ao" if dinheiro else "Retirar do"
        valor = simpledialog.askfloat("Ajuste Manual", f"Valor para {acao_nome} Patrimônio:", minvalue=0)
        if valor is None: return

        self.sistema.salvar_estado_atual()
        if dinheiro:
            j.patrimonio_atual += valor
            self.sistema.registrar_log(j.nome, "Ajuste Manual: Depósito", valor)
        else:
            j.patrimonio_atual -= valor
            self.sistema.registrar_log(j.nome, "Ajuste Manual: Saque", -valor)
        self.atualizar_tela()

    def ajuste_salario_direto(self):
        j = self.obter_jogador_selecionado()
        novo_salario = simpledialog.askfloat("Ajuste Manual", f"Digite o novo salário para {j.nome}:", initialvalue=j.salario, minvalue=0)
        if novo_salario is None: return

        self.sistema.salvar_estado_atual()
        antigo = j.salario
        j.salario = novo_salario
        self.sistema.registrar_log(j.nome, "Ajuste Manual: Alterou Salário", 0, f"De R${antigo:.2f} para R${novo_salario:.2f}")
        self.atualizar_tela()

    def executar_desfazer(self):
        if self.sistema.desfazer_ultima_acao():
            self.atualizar_tela()
            messagebox.showinfo("Sucesso", "Última ação desfeita com sucesso!")
        else:
            messagebox.showwarning("Aviso", "Não há ações registradas para desfazer.")

    def abrir_janela_edicao_jogador(self):
        """Abre uma sub-janela customizada para editar todos os parâmetros do jogador de uma vez."""
        j = self.obter_jogador_selecionado()
        
        janela_edicao = ctk.CTkToplevel(self)
        janela_edicao.title(f"Editar Dados - {j.nome}")
        janela_edicao.geometry("380x320")
        janela_edicao.grab_set()  # Bloqueia a tela de trás até terminar a edição
        
        ctk.CTkLabel(janela_edicao, text=f"Editando Perfil de {j.nome}", font=ctk.CTkFont(weight="bold")).pack(pady=10)
        
        # Inputs e Labels organizados
        frame_inputs = ctk.CTkFrame(janela_edicao)
        frame_inputs.pack(padx=15, pady=5, fill="both", expand=True)

        ctk.CTkLabel(frame_inputs, text="Nome:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        ent_nome = ctk.CTkEntry(frame_inputs)
        ent_nome.insert(0, j.nome)
        ent_nome.grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkLabel(frame_inputs, text="Salário:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        ent_salario = ctk.CTkEntry(frame_inputs)
        ent_salario.insert(0, str(j.salario))
        ent_salario.grid(row=1, column=1, padx=5, pady=5)

        ctk.CTkLabel(frame_inputs, text="Patrimônio Atual:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        ent_patr = ctk.CTkEntry(frame_inputs)
        ent_patr.insert(0, str(j.patrimonio_atual))
        ent_patr.grid(row=2, column=1, padx=5, pady=5)

        ctk.CTkLabel(frame_inputs, text="Membros Família:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        ent_fam = ctk.CTkEntry(frame_inputs)
        ent_fam.insert(0, str(j.membros_familia))
        ent_fam.grid(row=3, column=1, padx=5, pady=5)

        def salvar_edicao():
            try:
                self.sistema.salvar_estado_atual()
                j.nome = ent_nome.get()
                j.salario = float(ent_salario.get())
                j.patrimonio_atual = float(ent_patr.get())
                j.membros_familia = int(ent_fam.get())
                
                self.sistema.registrar_log(j.nome, "Dados Editados Manualmente", 0)
                self.atualizar_tela()
                janela_edicao.destroy()
            except ValueError:
                messagebox.showerror("Erro de Validação", "Por favor, insira valores numéricos válidos nos campos.")

        ctk.CTkButton(janela_edicao, text="💾 Salvar Alterações", fg_color="#27ae60", command=salvar_edicao).pack(pady=10)


# ==========================================
# INICIALIZAÇÃO DA APLICAÇÃO
# ==========================================

if __name__ == "__main__":
    sistema_partida = SistemaJogo()
    app = AppFinanceiro(sistema_partida)
    app.mainloop()
