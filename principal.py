import datetime
import streamlit as st

# Configuração da página do Streamlit
st.set_page_config(
    page_title="Gerenciador de Tabuleiro - Educação Financeira",
    page_icon="💰",
    layout="wide"
)

# ==========================================
# CLASSES DE NEGÓCIO (LÓGICA DO JOGO)
# ==========================================

class Investimento:
    def __init__(self, saldo_fixa=0.0):
        self.renda_fixa_acumulado = float(saldo_fixa)

    def investir_renda_fixa(self, valor: float):
        self.renda_fixa_acumulado += valor

    def rodar_renda_fixa(self) -> float:
        rendimento = self.renda_fixa_acumulado * 0.05
        self.renda_fixa_acumulado += rendimento
        return rendimento


class Jogador:
    def __init__(self, id, nome, salario, patrimonio_inicial, membros_familia, patrimonio_atual=None, saldo_fixa=0.0, parcelas_casa=None, saldo_carro=0.0, meses_carro=0):
        self.id = int(id)
        self.nome = str(nome)
        self.salario = float(salario)
        self.patrimonio_inicial = float(patrimonio_inicial)
        self.patrimonio_atual = float(patrimonio_inicial if patrimonio_atual is None else patrimonio_atual)
        self.membros_familia = int(membros_familia)
        self.investimento = Investimento(saldo_fixa)
        
        # Financiamento da Casa (SAC - Amortização Constante)
        self.parcelas_casa = list(parcelas_casa) if parcelas_casa is not None else []
        
        # Financiamento do Carro (Juros Compostos)
        self.saldo_carro = float(saldo_carro)
        self.meses_carro = int(meses_carro)
        
    @property
    def variacao_patrimonio(self) -> float:
        if self.patrimonio_inicial == 0:
            return 0.0
        return ((self.patrimonio_atual - self.patrimonio_inicial) / self.patrimonio_inicial) * 100

    def calcular_proxima_parcela_casa(self, taxa_juros=0.01) -> float:
        """Calcula a parcela da casa por Amortização Constante (SAC)"""
        if not self.parcelas_casa:
            return 0.0
        amortizacao_atual = self.parcelas_casa[0]
        saldo_devedor_atual = sum(self.parcelas_casa)
        juros = saldo_devedor_atual * taxa_juros
        return amortizacao_atual + juros

    def calcular_proxima_parcela_carro(self, taxa_juros=0.015) -> float:
        """Calcula a parcela do carro usando a fórmula de Juros Compostos (Price/Financiamento Padrão)"""
        if self.saldo_carro <= 0 or self.meses_carro <= 0:
            return 0.0
        # Fórmula da parcela com juros compostos: PMT = PV * [i * (1+i)^n] / [(1+i)^n - 1]
        i = taxa_juros
        n = self.meses_carro
        pmt = self.saldo_carro * (i * ((1 + i) ** n)) / (((1 + i) ** n) - 1)
        return pmt

    def processar_pagamentos_automaticos(self):
        """Paga as parcelas automaticamente no início ou fim da rodada do jogador"""
        logs_pagamento = []
        
        # 1. Pagamento Automático do Carro (Juros Compostos)
        if self.saldo_carro > 0 and self.meses_carro > 0:
            parcela_carro = self.calcular_proxima_parcela_carro(taxa_juros=0.015)
            self.patrimonio_atual -= parcela_carro
            
            # Atualiza o saldo devedor composto para a próxima rodada
            juros_gerados = self.saldo_carro * 0.015
            amortizado = parcela_carro - juros_gerados
            self.saldo_carro -= amortizado
            self.meses_carro -= 1
            
            if self.meses_carro <= 0 or self.saldo_carro < 1.0:
                self.saldo_carro = 0.0
                self.meses_carro = 0
            
            logs_pagamento.append(f"🚗 Carro Pago Auto: R${parcela_carro:.2f} (Restam {self.meses_carro}x)")

        # 2. Pagamento Automático da Casa (SAC - Amortização)
        if self.parcelas_casa:
            parcela_casa = self.calcular_proxima_parcela_casa(taxa_juros=0.01)
            self.patrimonio_atual -= parcela_casa
            self.parcelas_casa.pop(0) # Remove a amortização paga
            
            logs_pagamento.append(f"🏠 Casa Paga Auto: R${parcela_casa:.2f} (Restam {len(self.parcelas_casa)}x)")
            
        return logs_pagamento

    def exportar_estado(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "salario": self.salario,
            "patrimonio_inicial": self.patrimonio_inicial,
            "patrimonio_atual": self.patrimonio_atual,
            "membros_familia": self.membros_familia,
            "saldo_fixa": self.investimento.renda_fixa_acumulado,
            "parcelas_casa": self.parcelas_casa,
            "saldo_carro": self.saldo_carro,
            "meses_carro": self.meses_carro
        }


# ==========================================
# GERENCIAMENTO DE ESTADO DO STREAMLIT
# ==========================================

if "jogadores_dados" not in st.session_state:
    nomes_padrao = ["Ana", "Bruno", "Carlos", "Diana", "Eduardo", "Fernanda"]
    st.session_state.jogadores_dados = [
        {
            "id": i + 1,
            "nome": nome,
            "salario": 3000.0 + (i * 500),
            "patrimonio_inicial": 5000.0 + (i * 1000),
            "patrimonio_atual": 5000.0 + (i * 1000),
            "membros_familia": 2 + (i % 3),
            "saldo_fixa": 0.0,
            "parcelas_casa": [],
            "saldo_carro": 0.0,
            "meses_carro": 0
        }
        for i, nome in enumerate(nomes_padrao)
    ]

if "historico" not in st.session_state:
    st.session_state.historico = []

if "historico_estados" not in st.session_state:
    st.session_state.historico_estados = []

jogadores = [Jogador(**dados) for dados in st.session_state.jogadores_dados]


def salvar_estado_para_backup():
    copia = [{**d, "parcelas_casa": list(d["parcelas_casa"])} for d in st.session_state.jogadores_dados]
    st.session_state.historico_estados.append(copia)


def atualizar_session_state():
    st.session_state.jogadores_dados = [j.exportar_estado() for j in jogadores]


def registrar_log(jogador_nome: str, casa_ou_acao: str, valor: float, detalhe: str = ""):
    agora = datetime.datetime.now().strftime("%H:%M:%S")
    sinal = "+" if valor > 0 else ""
    val_str = f" ({sinal}R${valor:.2f})" if valor != 0 else ""
    msg = f"[{agora}] {jogador_nome} -> {casa_ou_acao}{val_str}. {detalhe}"
    st.session_state.historico.insert(0, msg)


# ==========================================
# INTERFACE VISUAL (STREAMLIT WEB)
# ==========================================

st.title("🏆 Gerenciador de Tabuleiro - Educação Financeira")

col_esquerda, col_direita = st.columns([3, 2])

with col_esquerda:
    st.subheader("👤 Status dos Jogadores")
    
    lider = max(jogadores, key=lambda x: x.variacao_patrimonio)
    lista_nomes = [j.nome for j in jogadores]
    nome_selecionado = st.radio("**Selecione o jogador da rodada atual:**", lista_nomes, horizontal=True)
    j_ativo = next(j for j in jogadores if j.nome == nome_selecionado)
    
    st.write("---")
    
    for j in jogadores:
        eh_lider = (lider and lider.id == j.id)
        cor_var = "green" if j.variacao_patrimonio >= 0 else "red"
        titulo_card = f"👑 {j.nome} (LÍDER)" if eh_lider else f"👤 {j.nome}"
        
        # Ícones de financiamento ativo
        ícones = ""
        if j.parcelas_casa: ícones += " 🏠[Financ. Casa]"
        if j.saldo_carro > 0: ícones += " 🚗[Financ. Carro]"
        
        with st.expander(f"{titulo_card} | Var: :{cor_var}[{j.variacao_patrimonio:+.1f}%] | Patr: R${j.patrimonio_atual:.2f}{ícones}", expanded=True):
            c1, c2, c3 = st.columns(3)
            c1.write(f"**Salário:** R${j.salario:.2f}")
            c2.write(f"**Família:** {j.membros_familia} pessoas")
            
            # Informações de dívidas futuras
            dividas = []
            if j.parcelas_casa:
                dividas.append(f"Próx. Casa: R${j.calcular_proxima_parcela_casa():.2f}")
            if j.saldo_carro > 0:
                dividas.append(f"Próx. Carro: R${j.calcular_proxima_parcela_carro():.2f}")
            
            if dividas:
                c3.write(" | ".join(dividas))
            else:
                c3.write(f"**Renda Fixa:** R${j.investimento.renda_fixa_acumulado:.2f}")

    st.subheader("🎲 Painel de Controle de Casas")
    
    # Executa os descontos automáticos antes de aplicar a nova casa da rodada
    def processar_rodada_com_segurança(acao_nome, valor_imediato=0.0, detalhe_acao=""):
        salvar_estado_para_backup()
        
        # 1. Paga automaticamente o que o jogador dever nesta rodada
        logs_pagos = j_ativo.processar_pagamentos_automaticos()
        
        # 2. Aplica a casa que ele acabou de cair
        j_ativo.patrimonio_atual += valor_imediato
        
        # Registra no log
        registrar_log(j_ativo.nome, acao_nome, valor_imediato, detalhe_acao)
        for log_auto in logs_pagos:
            registrar_log(j_ativo.nome, "Cobrança Automática de Turno", 0, log_auto)
            
        atualizar_session_state()
        st.rerun()

    grid1 = st.columns(3)
    grid2 = st.columns(3)
    grid3 = st.columns(3)
    grid4 = st.columns(3)
    
    # --- BOTÕES DAS CASAS COM COBRANÇA AUTOMÁTICA EM EMBUTIDA ---
    if grid1[0].button("🏠 C1: Comprar Casa (Amortização SAC)", use_container_width=True):
        valor_casa = j_ativo.salario * 12 # Casa custa 12x o Salário
        amortizacao_fixa = valor_casa / 20.0 # Parcelado em 20 rodadas de amortização constante
        j_ativo.parcelas_casa = [amortizacao_fixa] * 20
        processar_rodada_com_segurança("C1: Adquiriu Financiamento de Casa", 0, f"Valor do imóvel: R${valor_casa:.2f} financiado via Tabela SAC (20 parcelas).")

    if grid1[1].button("🚗 C2: Comprar Carro (Juros Compostos)", use_container_width=True):
        valor_carro = j_ativo.salario * 4.5
        j_ativo.saldo_carro = valor_carro
        j_ativo.meses_carro = 30 # 30 rodadas pagando juros compostos de 1.5% ao turno
        processar_rodada_com_segurança("C2: Comprou Carro Parcelado", 0, f"Valor original: R${valor_carro:.2f} parcelado em 30x com Juros Compostos de 1.5% por rodada.")

    if grid1[2].button("🏢 C3: Aluguel", use_container_width=True):
        custo = j_ativo.salario * 0.30
        processar_rodada_com_segurança("C3: Aluguel (30%)", -custo)

    if grid2[0].button("🛒 C4: Compra do Mês", use_container_width=True):
        custo = (j_ativo.salario * 0.05) * j_ativo.membros_familia
        processar_rodada_com_segurança("C4: Compra do Mês", -custo)

    if grid2[1].button("💡 C5: Luz", use_container_width=True):
        custo = (j_ativo.salario * 0.01) * j_ativo.membros_familia
        processar_rodada_com_segurança("C5: Conta de Luz", -custo)

    if grid2[2].button("💧 C6: Água", use_container_width=True):
        custo = (j_ativo.salario * 0.01) * j_ativo.membros_familia
        processar_rodada_com_segurança("C6: Conta de Água", -custo)

    if grid3[0].button("🐯 C7: Passar Turno Livre", use_container_width=True):
        processar_rodada_com_segurança("C7: Avançou no tabuleiro", 0, "Nenhum evento de casa, apenas quitou parcelas automáticas da vez.")

    if grid3[1].button("📈 C8: Aplicar Renda Fixa", use_container_width=True):
        aporte = j_ativo.salario * 0.5
        if j_ativo.patrimonio_atual >= aporte:
            j_ativo.patrimonio_atual -= aporte
            j_ativo.investimento.investir_renda_fixa(aporte)
            processar_rodada_com_segurança("C8: Investimento em Renda Fixa", 0, f"Alocou R${aporte:.2f}")
        else:
            st.error("Saldo insuficiente para investir.")

    if grid3[2].button("🔄 C8: Rodar Rendimento (5%)", use_container_width=True):
        rendeu = j_ativo.investimento.rodar_renda_fixa()
        processar_rodada_com_segurança("Rendimento de Ativos", rendeu, "Renda fixa rendeu 5%")

    if grid4[0].button("🚀 C9: Promoção (+25%)", use_container_width=True):
        j_ativo.salario *= 1.25
        processar_rodada_com_segurança("C9: Promoção de Cargo", 0, f"Novo Salário base: R${j_ativo.salario:.2f}")

    if grid4[1].button("📉 C10: Redução (-10%)", use_container_width=True):
        j_ativo.salario *= 0.90
        processar_rodada_com_segurança("C10: Crise na Empresa", 0, f"Novo Salário base: R${j_ativo.salario:.2f}")

    if grid4[2].button("🏥 C11: Hospital (-R$300)", use_container_width=True):
        processar_rodada_com_segurança("C11: Despesa de Saúde", -300)

    # Painel extra para ajustes manuais ou correções rápidas
    st.write("---")
    with st.expander("🛠️ Ajustes Técnicos Manuais e Sistema Undo"):
        c_ajuste, c_undo = st.columns(2)
        with c_ajuste:
            val_man = st.number_input("Valor de Correção (R$)", min_value=0.0, step=100.0)
            if st.button("Adicionar Saldo Manual"):
                salvar_estado_para_backup()
                j_ativo.patrimonio_atual += val_man
                registrar_log(j_ativo.nome, "Correção Manual de Caixa", val_man)
                atualizar_session_state()
                st.rerun()
        with c_undo:
            st.write("Errou o clique do botão?")
            if st.button("🔄 DESFAZER ÚLTIMA JOGADA", type="primary", use_container_width=True):
                if st.session_state.historico_estados:
                    st.session_state.jogadores_dados = st.session_state.historico_estados.pop()
                    st.session_state.historico.insert(0, "[Sistema] Jogada desfeita com sucesso.")
                    st.rerun()

with col_direita:
    st.subheader("🏆 Ranking de Patrimônio Líquido")
    jogadores_ordenados = sorted(jogadores, key=lambda x: x.variacao_patrimonio, reverse=True)
    
    for idx, j in enumerate(jogadores_ordenados, 1):
        medalha = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"{idx}º"
        st.write(f"{medalha} **{j.nome}** | Var: `{j.variacao_patrimonio:+.2f}%` (Patr: R${j.patrimonio_atual:.2f})")
    
    if lider:
        st.info(f"🎉 **Ganhador parcial:** {lider.nome}")

    st.write("---")
    st.subheader("📋 Histórico Completo de Eventos")
    if st.session_state.historico:
        st.text_area(label="Logs", value="\n".join(st.session_state.historico), height=400, disabled=True)
