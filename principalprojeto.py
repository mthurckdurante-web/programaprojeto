import streamlit as st
import pandas as pd

st.set_page_config(page_title="Jogo da Vida Real", page_icon="💰", layout="wide")

# ============================================================
# DADOS DOS 6 PERSONAGENS (conforme o PDF do jogo)
# ============================================================
PERSONAGENS = {
    "José Correria": {
        "classe": "E",
        "profissao": "Entregador de iFood",
        "estado_civil": "Solteiro",
        "filhos": 0,
        "salario": 1850.0,
        "despesas": {
            "Aluguel": 650, "Alimentação": 350, "Transporte": 400,
            "Contas": 180, "Internet": 80, "Outros": 100, "IPVA": 50
        },
        "sobra_pdf": 40,
    },
    "Patrícia Trabalhadora": {
        "classe": "D",
        "profissao": "Costureira",
        "estado_civil": "Solteira",
        "filhos": 2,
        "salario": 2300.0,
        "despesas": {
            "Aluguel": 700, "Alimentação": 550, "Transporte": 150,
            "Contas": 100, "Internet": 30, "Outros": 100, "Materiais": 200, "IPVA": 0
        },
        "sobra_pdf": 270,
    },
    "Barão Guimarães": {
        "classe": "A",
        "profissao": "Empresário",
        "estado_civil": "Casado",
        "filhos": 2,
        "salario": 50000.0,
        "despesas": {
            "Aluguel": 0, "Alimentação": 5000, "Transporte": 3000,
            "Contas": 2000, "Internet": 350, "Outros": 5000, "IPVA": 1000
        },
        "sobra_pdf": 27650,
    },
    "Doutora Fernanda": {
        "classe": "B",
        "profissao": "Executivo Corporate",
        "estado_civil": "Casado",
        "filhos": 2,
        "salario": 18000.0,
        "despesas": {
            "Aluguel": 4500, "Alimentação": 2500, "Transporte": 1400,
            "Contas": 900, "Internet": 200, "Outros": 1500, "IPVA": 350
        },
        "sobra_pdf": 4650,
    },
    "Chico Corretor": {
        "classe": "C",
        "profissao": "Corretor de imóveis",
        "estado_civil": "Casado",
        "filhos": 1,
        "salario": 6000.0,
        "despesas": {
            "Aluguel": 1800, "Alimentação": 1200, "Transporte": 600,
            "Contas": 450, "Internet": 120, "Outros": 800, "IPVA": 120
        },
        "sobra_pdf": 410,
    },
    "Marcos TI": {
        "classe": "C",
        "profissao": "TI",
        "estado_civil": "Solteiro",
        "filhos": 0,
        "salario": 6000.0,
        "despesas": {
            "Aluguel": 2000, "Alimentação": 1400, "Transporte": 550,
            "Contas": 350, "Internet": 180, "Outros": 900, "IPVA": 120
        },
        "sobra_pdf": 500,   },
}


# ============================================================
# FUNÇÕES
# ============================================================
def dinheiro(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def inicializar_jogadores():
    jogadores = {}
    for nome, personagem in PERSONAGENS.items():
        salario = float(personagem["salario"])
        jogadores[nome] = {
            "salario": salario,
            # O PDF não define patrimônio inicial; usamos um salário como referência.
            "saldo": salario,
            "patrimonio_inicial": salario,
            "casa": 0.0,
            "divida_casa": 0.0,
            "carro": 0.0,
            "divida_carro": 0.0,
            "historico": ["Início da partida: saldo inicial equivalente a um salário."],
            "meses": 0,
        }
    return jogadores


def registrar(nome, mensagem):
    st.session_state.jogadores[nome]["historico"].insert(0, mensagem)


def aplicar_evento(nome, descricao, valor):
    jogador = st.session_state.jogadores[nome]
    jogador["saldo"] += valor
    registrar(nome, f"{descricao}: {'+' if valor >= 0 else ''}{dinheiro(valor)}")


def patrimonio(nome):
    jogador = st.session_state.jogadores[nome]
    return (
        jogador["saldo"]
        + jogador["casa"]
        + jogador["carro"]
        - jogador["divida_casa"]
        - jogador["divida_carro"]
    )


def variacao_patrimonio(nome):
    jogador = st.session_state.jogadores[nome]
    inicial = jogador["patrimonio_inicial"]
    if inicial == 0:
        return 0.0
    return (patrimonio(nome) - inicial) / inicial * 100


# ============================================================
# INICIALIZAÇÃO DO ESTADO DA PARTIDA
# ============================================================
if "jogadores" not in st.session_state:
    st.session_state.jogadores = inicializar_jogadores()

# Se a lista de personagens mudar durante o desenvolvimento, completa os dados ausentes.
for nome_personagem, dados_personagem in PERSONAGENS.items():
    if nome_personagem not in st.session_state.jogadores:
        salario = float(dados_personagem["salario"])
        st.session_state.jogadores[nome_personagem] = {
            "salario": salario,
            "saldo": salario,
            "patrimonio_inicial": salario,
            "casa": 0.0,
            "divida_casa": 0.0,
            "carro": 0.0,
            "divida_carro": 0.0,
            "historico": ["Jogador adicionado à partida."],
            "meses": 0,
        }

# ============================================================
# INTERFACE
# ============================================================
st.title("💰 Jogo da Vida Real")
st.caption("Simulador financeiro para os seis personagens do tabuleiro.")

with st.sidebar:
    st.header("📘 Regras do simulador")
    st.markdown(
        """
        - **Casa:** custa 3.500% do salário (35 salários).
        - **Carro:** custa 400% do salário (4 salários).
        - **Promoção:** aumenta o salário em 15%.
        - **Rebaixamento:** reduz o salário em 15%.
        - **Acidente:** perde R$ 600.
        - **Supermercado:** paga R$ 250.
        - **Vitória:** maior aumento percentual do patrimônio.
        """
    )
    st.info(
        "O PDF não informa o patrimônio inicial nem o valor das parcelas. "
        "Por isso, o saldo inicial equivale a um salário e as parcelas são "
        "ajustáveis, sem juros."
    )

# Ranking
st.subheader("🏆 Classificação atual")
linhas_ranking = []
for nome_jogador in PERSONAGENS:
    jogador_ranking = st.session_state.jogadores[nome_jogador]
    linhas_ranking.append({
        "Personagem": nome_jogador,
        "Salário": dinheiro(jogador_ranking["salario"]),
        "Saldo disponível": dinheiro(jogador_ranking["saldo"]),
        "Patrimônio": dinheiro(patrimonio(nome_jogador)),
        "Aumento do patrimônio": f"{variacao_patrimonio(nome_jogador):.2f}%".replace(".", ","),
    })

df_ranking = pd.DataFrame(linhas_ranking)
df_ranking["_ordem"] = [
    variacao_patrimonio(n) for n in PERSONAGENS
]
df_ranking = df_ranking.sort_values("_ordem", ascending=False).drop(columns=["_ordem"])
st.dataframe(df_ranking, use_container_width=True, hide_index=True)

st.divider()

nome = st.selectbox("Escolha o jogador", list(PERSONAGENS.keys()))
p = PERSONAGENS[nome]
j = st.session_state.jogadores[nome]

st.header(nome)
st.write(
    f"**Classe {p['classe']}** · {p['profissao']} · "
    f"{p['estado_civil']} · Filhos: {p['filhos']}"
)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Salário atual", dinheiro(j["salario"]))
m2.metric("Saldo disponível", dinheiro(j["saldo"]))
m3.metric("Patrimônio atual", dinheiro(patrimonio(nome)))
m4.metric(
    "Aumento do patrimônio",
    f"{variacao_patrimonio(nome):.2f}%".replace(".", ",")
)

tab_eventos, tab_bens, tab_despesas, tab_historico = st.tabs(
    ["🎲 Eventos e ações", "🏠 Casa e carro", "🧾 Despesas mensais", "📜 Histórico"]
)

# ============================================================
# EVENTOS
# ============================================================
with tab_eventos:
    st.subheader("Ações do tabuleiro")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        if st.button("💵 Receber salário", use_container_width=True):
            aplicar_evento(nome, "Salário recebido", j["salario"])
            st.rerun()

        if st.button("📈 Foi promovido (+15%)", use_container_width=True):
            aumento = j["salario"] * 0.15
            j["salario"] += aumento
            registrar(nome, f"Promoção: salário aumentou {dinheiro(aumento)} (15%).")
            st.rerun()

    with c2:
        if st.button("📉 Foi rebaixado (−15%)", use_container_width=True):
            reducao = j["salario"] * 0.15
            j["salario"] -= reducao
            registrar(nome, f"Rebaixamento: salário diminuiu {dinheiro(reducao)} (15%).")
            st.rerun()

        if st.button("🚑 Sofreu acidente (−R$ 600)", use_container_width=True):
            aplicar_evento(nome, "Acidente", -600)
            st.rerun()

    with c3:
        if st.button("🛒 Compras de supermercado (−R$ 250)", use_container_width=True):
            aplicar_evento(nome, "Compras de supermercado", -250)
            st.rerun()

        if st.button("🧾 Pagar despesas fixas do mês", use_container_width=True):
            total_despesas = sum(p["despesas"].values())
            aplicar_evento(nome, "Despesas fixas mensais", -total_despesas)
            j["meses"] += 1
            st.rerun()

    st.caption(
        "O pagamento das despesas fixas desconta os valores do perfil. "
        "O supermercado é um evento separado."
    )

# ============================================================
# CASA E CARRO
# ============================================================
with tab_bens:
    st.subheader("Compra e amortização de bens")
    preco_casa = j["salario"] * 35
    preco_carro = j["salario"] * 4
    coluna_casa, coluna_carro = st.columns(2)

    with coluna_casa:
        st.markdown("### 🏠 Casa")
        st.write(f"Preço da casa: **{dinheiro(preco_casa)}**")
        st.write(f"Valor do bem: {dinheiro(j['casa'])}")
        st.write(f"Dívida restante: {dinheiro(j['divida_casa'])}")

        parcela_casa = st.number_input(
            "Parcela da casa (R$)",
            min_value=1.0,
            value=float(max(1, round(j["salario"] * 0.10, 2))),
            step=50.0,
            key=f"parcela_casa_{nome}",
        )

        if st.button("Comprar casa", key=f"comprar_casa_{nome}", use_container_width=True):
            if j["casa"] == 0 and j["divida_casa"] == 0:
                j["casa"] = preco_casa
                j["divida_casa"] = preco_casa
                registrar(nome, f"Comprou uma casa de {dinheiro(preco_casa)} financiada.")
            else:
                st.warning("Este jogador já possui uma casa ou financiamento.")
            st.rerun()

        if st.button("Pagar parcela da casa", key=f"pagar_casa_{nome}", use_container_width=True):
            if j["divida_casa"] <= 0:
                st.warning("Este jogador não tem dívida de casa.")
            elif j["saldo"] < min(parcela_casa, j["divida_casa"]):
                st.error("Saldo insuficiente para pagar essa parcela.")
            else:
                valor_pago = min(parcela_casa, j["divida_casa"])
                j["saldo"] -= valor_pago
                j["divida_casa"] -= valor_pago
                registrar(nome, f"Amortização da casa: pagou {dinheiro(valor_pago)}.")
            st.rerun()
            with coluna_carro:



    
        st.markdown("### 🚗 Carro")
        st.write(f"Preço do carro: **{dinheiro(preco_carro)}**")
        st.write(f"Valor do bem: {dinheiro(j['carro'])}")
        st.write(f"Dívida restante: {dinheiro(j['divida_carro'])}")

        parcela_carro = st.number_input(
            "Parcela do carro (R$)",
            min_value=1.0,
            value=float(max(1, round(j["salario"] * 0.20, 2))),
            step=50.0,
            key=f"parcela_carro_{nome}",
        )

        if st.button("Comprar carro", key=f"comprar_carro_{nome}", use_container_width=True):
            if j["carro"] == 0 and j["divida_carro"] == 0:
                j["carro"] = preco_carro
                j["divida_carro"] = preco_carro
                registrar(nome, f"Comprou um carro de {dinheiro(preco_carro)} financiado.")
            else:
                st.warning("Este jogador já possui um carro ou financiamento.")
            st.rerun()

        if st.button("Pagar parcela do carro", key=f"pagar_carro_{nome}", use_container_width=True):
            if j["divida_carro"] <= 0:
                st.warning("Este jogador não tem dívida de carro.")
            elif j["saldo"] < min(parcela_carro, j["divida_carro"]):
                st.error("Saldo insuficiente para pagar essa parcela.")
            else:
                valor_pago = min(parcela_carro, j["divida_carro"])
                j["saldo"] -= valor_pago
                j["divida_carro"] -= valor_pago
                registrar(nome, f"Amortização do carro: pagou {dinheiro(valor_pago)}.")
            st.rerun()

# ============================================================
# DESPESAS E HISTÓRICO
# ============================================================
with tab_despesas:
    st.subheader("Despesas registradas no perfil")
    df_despesas = pd.DataFrame([
        {"Despesa": despesa, "Valor mensal": dinheiro(valor)}
        for despesa, valor in p["despesas"].items()
    ])
    st.dataframe(df_despesas, use_container_width=True, hide_index=True)
    st.write(f"**Total das despesas cadastradas:** {dinheiro(sum(p['despesas'].values()))}")
    st.write(f"**Sobra mensal indicada no PDF:** {dinheiro(p['sobra_pdf'])}")
    st.caption(
        "A sobra mensal é mostrada como referência. O botão de despesas fixas "
        "desconta os valores listados individualmente no perfil."
    )

with tab_historico:
    st.subheader("Histórico de ações")
    historico = j["historico"]
    if historico:
        for item in historico:
            st.write(f"• {item}")
    else:
        st.info("Nenhuma ação registrada.")

st.divider()
if st.button("🔄 Reiniciar partida inteira", type="secondary"):
    st.session_state.jogadores = inicializar_jogadores()
    st.rerun()

st.caption(
    "Patrimônio = saldo disponível + valor dos bens − dívidas restantes. "
    "O ranking usa a variação percentual em relação ao patrimônio inicial."
)
