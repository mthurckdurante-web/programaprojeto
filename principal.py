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
        self.renda_fixa_acumulado = saldo_fixa

    def investir_renda_fixa(self, valor: float):
        self.renda_fixa_acumulado += valor

    def rodar_renda_fixa(self) -> float:
        rendimento = self.renda_fixa_acumulado * 0.05
        self.renda_fixa_acumulado += rendimento
        return rendimento


class Jogador:
    def __init__(self, id_jog: int, nome: str, salario: float, patrimonio_inicial: float, membros_familia: int, patrimonio_atual=None, saldo_fixa=0.0):
        self.id = id_jog
        self.nome = nome
        self.salario = salario
        self.patrimonio_inicial = patrimonio_inicial
        self.patrimonio_atual = patrimonio_inicial if patrimonio_atual is None else patrimonio_atual
        self.membros_familia = membros_familia
        self.investimento = Investimento(saldo_fixa)
        
    @property
    def variacao_patrimonio(self) -> float:
        if self.patrimonio_inicial == 0:
            return 0.0
        return ((self.patrimonio_atual - self.patrimonio_inicial) / self.patrimonio_inicial) * 100

    def exportar_estado(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "salario": self.salario,
            "patrimonio_inicial": self.patrimonio_inicial,
            "patrimonio_atual": self.patrimonio_atual,
            "membros_familia": self.membros_familia,
            "saldo_fixa": self.investimento.renda_fixa_acumulado
        }


# ==========================================
# GERENCIAMENTO DE ESTADO DO STREAMLIT
# ==========================================

# Força a limpeza se a estrutura estiver corrompida
if "jogadores_dados" in st.session_state and not isinstance(st.session_state.jogadores_dados, list):
    st.session_state.clear()

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
            "saldo_fixa": 0.0
        }
        for i, nome in enumerate(nomes_padrao)
    ]

if "historico" not in st.session_state:
    st.session_state.historico = []

if "historico_estados" not in st.session_state:
    st.session_state.historico_estados = []

# Reconstrói os objetos de forma segura
jogadores = []
for dados in st.session_state.jogadores_dados:
    if isinstance(dados, dict) and "id" in dados:
        jogadores.append(Jogador(**dados))

if not jogadores:
    st.session_state.clear()
    st.rerun()


def salvar_estado_para_backup():
    copia = [dados.copy() for dados in st.session_state.jogadores_dados]
    st.session_state.historico_estados.append(copia)
    if len(st.session_state.historico_estados) > 20:
        st.session_state.historico_estados.pop(0)


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
    
    lider = max(jogadores, key=lambda x: x.variacao_patrimonio) if jogadores else None
    
    lista_nomes = [j.nome for j in jogadores]
    nome_selecionado = st.radio("**Selecione o jogador que caiu na casa:**", lista_nomes, horizontal=True)
    j_ativo = next(j for j in jogadores if j.nome == nome_selecionado)
    
    st.write("---")
    
    for j in jogadores:
        eh_lider = (lider and lider.id == j.id)
        cor_var = "green" if j.variacao_patrimonio >= 0 else "red"
        titulo_card = f"👑 {j.nome} (LÍDER)" if eh_lider else f"👤 {j.nome}"
        
        with st.expander(f"{titulo_card} | Var: :{cor_var}[{j.variacao_patrimonio:+.1f}%] | Patr: R${j.patrimonio_atual:.2f}", expanded=True):
            c1, c2, c3 = st.columns(3)
            c1.write(f"**Salário:** R${j.salario:.2f}")
            c2.write(f"**Família:** {j.membros_familia} pessoas")
            c3.write(f"**Renda Fixa:** R${j.investimento.renda_fixa_acumulado:.2f}")

    st.subheader("🎲 Painel de Controle de Casas")
    tab_casas, tab_ajustes = st.tabs(["Casas do Tabuleiro", "Ajustes Manuais e Edição"])
    
    with tab_casas:
        grid1 = st.columns(3)
        grid2 = st.columns(3)
        grid3 = st.columns(3)
        grid4 = st.columns(3)
        
        if grid1[0].button("⚠️ C1: Juros 3000%", use_container_width=True):
            salvar_estado_para_backup()
            impacto = j_ativo.salario * 2
            j_ativo.patrimonio_atual -= impacto
            registrar_log(j_ativo.nome, "C1: Juros 3000%", -impacto, "Penalidade aplicada")
            atualizar_session_state()
            st.rerun()

        if grid1[1].button("🚗 C2: Comprar Carro", use_container_width=True):
            salvar_estado_para_backup()
            valor_carro = j_ativo.salario * 4.5
            j_ativo.patrimonio_atual -= valor_carro
            registrar_log(j_ativo.nome, "C2: Comprou Carro (450% Salário)", -valor_carro)
            atualizar_session_state()
            st.rerun()

        if grid1[2].button("🏠 C3: Aluguel", use_container_width=True):
            salvar_estado_para_backup()
            custo = j_ativo.salario * 0.30
            j_ativo.patrimonio_atual -= custo
            registrar_log(j_ativo.nome, "C3: Aluguel (30%)", -custo)
            atualizar_session_state()
            st.rerun()

        if grid2[0].button("🛒 C4: Compra do Mês", use_container_width=True):
            salvar_estado_para_backup()
            porcentagem = 0.05 * j_ativo.membros_familia
            custo = j_ativo.salario * porcentagem
            j_ativo.patrimonio_atual -= custo
            registrar_log(j_ativo.nome, f"C4: Compra do Mês ({porcentagem*100:.0f}%)", -custo)
            atualizar_session_state()
            st.rerun()

        if grid2[1].button("💡 C5: Luz", use_container_width=True):
            salvar_estado_para_backup()
            porcentagem = 0.01 * j_ativo.membros_familia
            custo = j_ativo.salario * porcentagem
            j_ativo.patrimonio_atual -= custo
            registrar_log(j_ativo.nome, "C5: Conta de Luz", -custo)
            atualizar_session_state()
            st.rerun()

        if grid2[2].button("💧 C6: Água", use_container_width=True):
            salvar_estado_para_backup()
            porcentagem = 0.01 * j_ativo.membros_familia
            custo = j_ativo.salario * porcentagem
            j_ativo.patrimonio_atual -= custo
            registrar_log(j_ativo.nome, "C6: Conta de Água", -custo)
            atualizar_session_state()
            st.rerun()

        if grid3[0].button("🐯 C7: Tigrinho", use_container_width=True):
            st.info("Use a aba de Ajustes Manuais para adicionar valores livres de ganho ou perda.")

        if grid3[1].button("📈 C8: Aplicar Renda Fixa", use_container_width=True):
            salvar_estado_para_backup()
            aporte = j_ativo.salario * 0.5
            if j_ativo.patrimonio_atual >= aporte:
                j_ativo.patrimonio_atual -= aporte
                j_ativo.investimento.investir_renda_fixa(aporte)
                registrar_log(j_ativo.nome, "C8: Aplicou Renda Fixa", -aporte)
                atualizar_session_state()
                st.rerun()

        if grid3[2].button("🔄 C8: Render Fixa (5%)", use_container_width=True):
            salvar_estado_para_backup()
            rendeu = j_ativo.investimento.rodar_renda_fixa()
            if rendeu > 0:
                j_ativo.patrimonio_atual += rendeu
                registrar_log(j_ativo.nome, "Rendimento Renda Fixa (+5%)", rendeu)
                atualizar_session_state()
                st.rerun()

        if grid4[0].button("🚀 C9: Promoção (+25%)", use_container_width=True):
            salvar_estado_para_backup()
            aumento = j_ativo.salario * 0.25
            j_ativo.salario += aumento
            registrar_log(j_ativo.nome, "C9: Promoção de Cargo", 0)
            atualizar_session_state()
            st.rerun()

        if grid4[1].button("📉 C10: Redução (-10%)", use_container_width=True):
            salvar_estado_para_backup()
            queda = j_ativo.salario * 0.10
            j_ativo.salario -= queda
            registrar_log(j_ativo.nome, "C10: Redução Salarial", 0)
            atualizar_session_state()
            st.rerun()

        if grid4[2].button("🏥 C11: Hospital (-R$300)", use_container_width=True):
            salvar_estado_para_backup()
            j_ativo.patrimonio_atual -= 300
            registrar_log(j_ativo.nome, "C11: Despesa Hospitalar", -300)
            atualizar_session_state()
            st.rerun()

    with tab_ajustes:
        with st.form("form_ajustes"):
            val_ajuste = st.number_input("Valor do Ajuste (R$)", min_value=0.0, step=100.0)
            tipo_operacao = st.selectbox("Operação", ["Adicionar ao Patrimônio", "Retirar do Patrimônio", "Alterar Salário Direto"])
            botao_submeter = st.form_submit_button("Confirmar Ajuste Manual")
            
            if botao_submeter:
                salvar_estado_para_backup()
                if tipo_operacao == "Adicionar ao Patrimônio":
                    j_ativo.patrimonio_atual += val_ajuste
                    registrar_log(j_ativo.nome, "Ajuste Manual: Depósito", val_ajuste)
                elif tipo_operacao == "Retirar do Patrimônio":
                    j_ativo.patrimonio_atual -= val_ajuste
                    registrar_log(j_ativo.nome, "Ajuste Manual: Saque", -val_ajuste)
                elif tipo_operacao == "Alterar Salário Direto":
                    antigo = j_ativo.salario
                    j_ativo.salario = val_ajuste
                    registrar_log(j_ativo.nome, "Ajuste Manual: Alteração Salarial", 0)
                
                atualizar_session_state()
                st.rerun()

        if st.button("🔄 DESFAZER ÚLTIMA AÇÃO (UNDO)", type="primary", use_container_width=True):
            if st.session_state.historico_estados:
                st.session_state.jogadores_dados = st.session_state.historico_estados.pop()
                st.session_state.historico.insert(0, "[Sistema] Ação Desfeita.")
                st.rerun()

with col_direita:
    st.subheader("🏆 Ranking Atual")
    jogadores_ordenados = sorted(jogadores, key=lambda x: x.variacao_patrimonio, reverse=True)
    
    for idx, j in enumerate(jogadores_ordenados, 1):
        medalha = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"{idx}º"
        st.write(f"{medalha} **{j.nome}** | Var: `{j.variacao_patrimonio:+.2f}%` (Patr: R${j.patrimonio_atual:.2f})")
    
    if lider:
        st.info(f"🎉 **Vencedor Atual:** {lider.nome}")

    st.write("---")
    st.subheader("📋 Histórico de Eventos")
    if st.session_state.historico:
        st.text_area(label="Logs", value="\n".join(st.session_state.historico), height=300, disabled=True)
