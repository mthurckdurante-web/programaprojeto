import datetime
import pandas as pd
import streamlit as st

# Configuração da página do Streamlit
st.set_page_config(
    page_title="Gerenciador de Tabuleiro - Educação Financeira",
    page_icon="💰",
    layout="wide"
)

DATA_INICIAL = datetime.date(2026, 1, 1)

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
    def __init__(self, id, nome, salario, patrimonio_inicial, membros_familia,
                 patrimonio_atual=None, saldo_fixa=0.0, parcelas_casa=None,
                 saldo_carro=0.0, meses_carro=0, tem_carro=False, data_jogo=None):
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
        # Continua True mesmo depois de quitar o financiamento (o carro segue gerando manutenção)
        self.tem_carro = bool(tem_carro)

        # Calendário do jogo: cada jogador tem sua própria data
        self.data_jogo = data_jogo if data_jogo is not None else DATA_INICIAL

    @property
    def variacao_patrimonio(self) -> float:
        if self.patrimonio_inicial == 0:
            return 0.0
        return ((self.patrimonio_atual - self.patrimonio_inicial) / self.patrimonio_inicial) * 100

    # ------------------------------------------
    # SALÁRIO E CONTAS DESCONTADAS DO SALÁRIO
    # ------------------------------------------
    def contas_do_salario(self):
        """Contas menores que são descontadas do salário todo dia 1."""
        contas = [
            ("🛒 Compra do Mês", self.salario * 0.05 * self.membros_familia),
            ("💡 Luz", self.salario * 0.01 * self.membros_familia),
            ("💧 Água", self.salario * 0.01 * self.membros_familia),
        ]
        if self.tem_carro:
            contas.append(("🔧 Reparo/Manutenção do Carro", self.salario * 0.03))
        return contas

    def salario_liquido_previsto(self) -> float:
        return self.salario - sum(valor for _, valor in self.contas_do_salario())

    def dias_para_proximo_salario(self) -> int:
        proximo = (self.data_jogo.replace(day=1) + datetime.timedelta(days=32)).replace(day=1)
        return (proximo - self.data_jogo).days

    def processar_virada_mes(self):
        """Cai o salário e desconta as contas do salário (executado todo dia 1)."""
        logs = []
        mes_ref = self.data_jogo.strftime("%m/%Y")

        self.patrimonio_atual += self.salario
        logs.append(f"💰 Dia 01/{mes_ref}: salário recebido +R${self.salario:.2f}")

        total_descontos = 0.0
        for nome_conta, valor in self.contas_do_salario():
            self.patrimonio_atual -= valor
            total_descontos += valor
            logs.append(f"   ➖ {nome_conta}: -R${valor:.2f}")

        logs.append(f"   ✅ Líquido do mês: R${self.salario - total_descontos:.2f}")
        return logs

    def avancar_dias(self, dias: int):
        """Avança o calendário do jogador; a cada dia 1 que passa, paga o salário."""
        logs = []
        for _ in range(int(dias)):
            self.data_jogo += datetime.timedelta(days=1)
            if self.data_jogo.day == 1:
                logs.extend(self.processar_virada_mes())
        return logs

    # ------------------------------------------
    # FINANCIAMENTOS
    # ------------------------------------------
    def calcular_proxima_parcela_casa(self, taxa_juros=0.01) -> float:
        """Calcula a parcela da casa por Amortização Constante (SAC)"""
        if not self.parcelas_casa:
            return 0.0
        amortizacao_atual = self.parcelas_casa[0]
        saldo_devedor_atual = sum(self.parcelas_casa)
        juros = saldo_devedor_atual * taxa_juros
        return amortizacao_atual + juros

    def tabela_amortizacao_casa(self, taxa_juros=0.01):
        """Reconstrói a tabela completa das parcelas restantes do financiamento da casa (SAC)."""
        linhas = []
        restantes = list(self.parcelas_casa)
        for i in range(len(restantes)):
            saldo_devedor = sum(restantes[i:])
            amortizacao = restantes[i]
            juros = saldo_devedor * taxa_juros
            parcela = amortizacao + juros
            linhas.append({
                "Parcela restante": i + 1,
                "Saldo Devedor": round(saldo_devedor, 2),
                "Amortização": round(amortizacao, 2),
                "Juros": round(juros, 2),
                "Valor da Parcela": round(parcela, 2),
            })
        return linhas

    def calcular_proxima_parcela_carro(self, taxa_juros=0.015) -> float:
        """Calcula a parcela do carro usando a fórmula de Juros Compostos (Price/Financiamento Padrão)"""
        if self.saldo_carro <= 0 or self.meses_carro <= 0:
            return 0.0
        # PMT = PV * [i * (1+i)^n] / [(1+i)^n - 1]
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
            self.parcelas_casa.pop(0)  # Remove a amortização paga

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
            "meses_carro": self.meses_carro,
            "tem_carro": self.tem_carro,
            "data_jogo": self.data_jogo,
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
            "meses_carro": 0,
            "tem_carro": False,
            "data_jogo": DATA_INICIAL,
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
# BARRA LATERAL (CONFIGURAÇÃO DO CALENDÁRIO)
# ==========================================

st.sidebar.header("📅 Calendário do Jogo")
st.sidebar.slider(
    "Dias que passam a cada jogada",
    min_value=1, max_value=31, value=10, key="dias_por_turno",
    help="A cada jogada o calendário do jogador avança esse número de dias. "
         "Sempre que passar pelo dia 1, o salário cai e as contas do salário são descontadas."
)
st.sidebar.caption(
    "💰 Todo dia 1: cai o salário e são descontados automaticamente "
    "Compra do Mês, Luz, Água e (se tiver carro) Reparo/Manutenção do Carro."
)

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
        icones = ""
        if j.parcelas_casa:
            icones += " 🏠[Financ. Casa]"
        if j.saldo_carro > 0:
            icones += " 🚗[Financ. Carro]"

        with st.expander(f"{titulo_card} | Var: :{cor_var}[{j.variacao_patrimonio:+.1f}%] | Patr: R${j.patrimonio_atual:.2f}{icones}", expanded=True):
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

            # Calendário e previsão do próximo salário
            d1, d2 = st.columns(2)
            d1.write(f"📅 **Data:** {j.data_jogo.strftime('%d/%m/%Y')}")
            d2.write(f"💰 **Próximo salário em:** {j.dias_para_proximo_salario()} dia(s)")

            descontos_txt = " · ".join(f"{nome_conta} R${valor:.2f}" for nome_conta, valor in j.contas_do_salario())
            st.caption(f"Descontos do salário no dia 1: {descontos_txt}")
            st.caption(f"💵 Líquido previsto: R${j.salario_liquido_previsto():.2f}")

            # Botão para abrir/fechar a tabela de amortização da casa (SAC)
            if j.parcelas_casa:
                if st.button(f"📊 Ver Amortização - {j.nome}", key=f"btn_amort_{j.id}"):
                    st.session_state[f"mostrar_amort_{j.id}"] = not st.session_state.get(f"mostrar_amort_{j.id}", False)

                if st.session_state.get(f"mostrar_amort_{j.id}", False):
                    tabela = j.tabela_amortizacao_casa()
                    st.dataframe(pd.DataFrame(tabela), use_container_width=True, hide_index=True)

    st.subheader("🎲 Painel de Controle de Casas")

    # Executa os descontos automáticos antes de aplicar a nova casa da rodada
    def processar_rodada_com_segurança(acao_nome, valor_imediato=0.0, detalhe_acao="", dias=None):
        salvar_estado_para_backup()

        # 1. Paga automaticamente o que o jogador dever nesta rodada (parcelas)
        logs_pagos = j_ativo.processar_pagamentos_automaticos()

        # 2. Aplica a casa que ele acabou de cair
        j_ativo.patrimonio_atual += valor_imediato

        # 3. Avança o calendário (se passar pelo dia 1, cai o salário e desconta as contas)
        dias_avanco = dias if dias is not None else st.session_state.dias_por_turno
        logs_calendario = j_ativo.avancar_dias(dias_avanco)

        # Registra no log
        registrar_log(j_ativo.nome, acao_nome, valor_imediato, detalhe_acao)
        for log_auto in logs_pagos:
            registrar_log(j_ativo.nome, "Cobrança Automática de Turno", 0, log_auto)
        for log_cal in logs_calendario:
            registrar_log(j_ativo.nome, "📅 Virada de Mês", 0, log_cal.strip())

        atualizar_session_state()
        st.rerun()

    grid1 = st.columns(3)
    grid2 = st.columns(3)
    grid3 = st.columns(3)

    # --- BOTÕES DAS CASAS ---
    # Obs.: Compra do Mês, Luz e Água agora são descontadas do salário (dia 1)
    if grid1[0].button("🏠 C1: Comprar Casa (Amortização SAC)", use_container_width=True):
        valor_casa = j_ativo.salario * 12  # Casa custa 12x o Salário
        amortizacao_fixa = valor_casa / 20.0  # Parcelado em 20 rodadas de amortização constante
        j_ativo.parcelas_casa = [amortizacao_fixa] * 20
        processar_rodada_com_segurança("C1: Adquiriu Financiamento de Casa", 0, f"Valor do imóvel: R${valor_casa:.2f} financiado via Tabela SAC (20 parcelas).")

    if grid1[1].button("🚗 C2: Comprar Carro (Juros Compostos)", use_container_width=True):
        valor_carro = j_ativo.salario * 4.5
        j_ativo.saldo_carro = valor_carro
        j_ativo.meses_carro = 30  # 30 rodadas pagando juros compostos de 1.5% ao turno
        j_ativo.tem_carro = True  # A partir de agora entra o reparo do carro no desconto do salário
        processar_rodada_com_segurança("C2: Comprou Carro Parcelado", 0, f"Valor original: R${valor_carro:.2f} parcelado em 30x com Juros Compostos de 1.5% por rodada.")

    if grid1[2].button("🏢 C3: Aluguel", use_container_width=True):
        custo = j_ativo.salario * 0.30
        processar_rodada_com_segurança("C3: Aluguel (30%)", -custo)

    if grid2[0].button("🐯 C7: Passar Turno Livre", use_container_width=True):
        processar_rodada_com_segurança("C7: Avançou no tabuleiro", 0, "Nenhum evento de casa, apenas quitou parcelas automáticas da vez.")

    if grid2[1].button("📈 C8: Aplicar Renda Fixa", use_container_width=True):
        aporte = j_ativo.salario * 0.5
        if j_ativo.patrimonio_atual >= aporte:
            j_ativo.patrimonio_atual -= aporte
            j_ativo.investimento.investir_renda_fixa(aporte)
            processar_rodada_com_segurança("C8: Investimento em Renda Fixa", 0, f"Alocou R${aporte:.2f}")
        else:
            st.error("Saldo insuficiente para investir.")

    if grid2[2].button("🔄 C8: Rodar Rendimento (5%)", use_container_width=True):
        rendeu = j_ativo.investimento.rodar_renda_fixa()
        processar_rodada_com_segurança("Rendimento de Ativos", rendeu, "Renda fixa rendeu 5%")

    if grid3[0].button("🚀 C9: Promoção (+25%)", use_container_width=True):
        j_ativo.salario *= 1.25
        processar_rodada_com_segurança("C9: Promoção de Cargo", 0, f"Novo Salário base: R${j_ativo.salario:.2f}")

    if grid3[1].button("📉 C10: Redução (-10%)", use_container_width=True):
        j_ativo.salario *= 0.90
        processar_rodada_com_segurança("C10: Crise na Empresa", 0, f"Novo Salário base: R${j_ativo.salario:.2f}")

    if grid3[2].button("🏥 C11: Hospital (-R$300)", use_container_width=True):
        processar_rodada_com_segurança("C11: Despesa de Saúde", -300)

    # Pula direto para o próximo dia 1 (útil para testar ou avançar o mês)
    if st.button("📅 Avançar até o dia 1 (receber salário)", use_container_width=True):
        dias_ate_salario = j_ativo.dias_para_proximo_salario()
        processar_rodada_com_segurança(
            "Avançou até o dia 1", 0,
            f"Calendário avançou {dias_ate_salario} dia(s) até o próximo salário.",
            dias=dias_ate_salario,
        )

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
