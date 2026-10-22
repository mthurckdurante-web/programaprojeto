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
        "patrimônio": 7300.0,
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
        "patrimônio": 2300.0,
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
        "patrimônio": 5450000.0,
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
        "patrimônio": 210000.0,
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
        "patrimônio": 57000.0,
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
        "patrimônio": 70000.0,
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
    """Cria os jogadores com bens e patrimônio inicial."""
    jogadores = {}

    bens_iniciais = {
        "José Correria": {
            "saldo": 300.0, "reserva": 0.0, "casa": 0.0,
            "carro": 0.0, "moto": 7000.0, "bicicleta": 0.0,
        },
        "Patrícia Trabalhadora": {
            "saldo": 1500.0, "reserva": 0.0, "casa": 0.0,
            "carro": 0.0, "moto": 0.0, "bicicleta": 800.0,
        },
        "Barão Guimarães": {
            "saldo": 0.0, "reserva": 2000000.0, "casa": 3000000.0,
            "carro": 450000.0, "moto": 0.0, "bicicleta": 0.0,
        },
        "Doutora Fernanda": {
            "saldo": 0.0, "reserva": 80000.0, "casa": 0.0,
            "carro": 130000.0, "moto": 0.0, "bicicleta": 0.0,
        },
        "Chico Corretor": {
            "saldo": 0.0, "reserva": 12000.0, "casa": 0.0,
            "carro": 45000.0, "moto": 0.0, "bicicleta": 0.0,
        },
        "Marcos TI": {
            "saldo": 0.0, "reserva": 20000.0, "casa": 0.0,
            "carro": 50000.0, "moto": 0.0, "bicicleta": 0.0,
        },
    }

    for nome, personagem in PERSONAGENS.items():
        salario = float(personagem["salario"])
        patrimonio_inicial = float(personagem["patrimônio"])
        bens = bens_iniciais.get(nome, {})

        jogador = {
            "salario": salario,
            "saldo": float(bens.get("saldo", 0.0)),
            "reserva": float(bens.get("reserva", 0.0)),
            "patrimonio_inicial": patrimonio_inicial,
            "casa": float(bens.get("casa", 0.0)),
            "divida_casa": 0.0,
            "carro": float(bens.get("carro", 0.0)),
            "moto": float(bens.get("moto", 0.0)),
            "bicicleta": float(bens.get("bicicleta", 0.0)),
            "divida_carro": 0.0,
            "historico": [
                "Início da partida: patrimônio inicial e bens cadastrados."
            ],
            "meses": 0,
        }

        jogadores[nome] = jogador

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
        float(jogador.get("saldo", 0.0))
        + float(jogador.get("reserva", 0.0))
        + float(jogador.get("casa", 0.0))
        + float(jogador.get("carro", 0.0))
        + float(jogador.get("moto", 0.0))
        + float(jogador.get("bicicleta", 0.0))
        - float(jogador.get("divida_casa", 0.0))
        - float(jogador.get("divida_carro", 0.0))
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
# A versão força uma única reinicialização dos dados antigos para aplicar
# os patrimônios e bens iniciais corrigidos. Depois, a partida é preservada.
VERSAO_DADOS = 2
if (
    "jogadores" not in st.session_state
    or st.session_state.get("versao_dados") != VERSAO_DADOS
):
    st.session_state.jogadores = inicializar_jogadores()
    st.session_state.versao_dados = VERSAO_DADOS

# Compatibilidade com jogadores salvos em versões anteriores.
for nome_personagem, dados_personagem in PERSONAGENS.items():
    if nome_personagem not in st.session_state.jogadores:
        novo_jogador = inicializar_jogadores()[nome_personagem]
        st.session_state.jogadores[nome_personagem] = novo_jogador

for jogador_existente in st.session_state.jogadores.values():
    jogador_existente.setdefault("reserva", 0.0)
    jogador_existente.setdefault("moto", 0.0)
    jogador_existente.setdefault("bicicleta", 0.0)
    jogador_existente.setdefault("casa", 0.0)
    jogador_existente.setdefault("carro", 0.0)
    jogador_existente.setdefault("divida_casa", 0.0)
    jogador_existente.setdefault("divida_carro", 0.0)

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
# EVENTOS DO TABULEIRO (30 casas)
# ============================================================
def executar_casa(numero, nome_jogador):
    jogador = st.session_state.jogadores[nome_jogador]
    saldo = jogador["saldo"]

    if numero == 1:
        # O pagamento corresponde ao salário atual do personagem escolhido.
        salario_atual = jogador["salario"]
        aplicar_evento(
            nome_jogador,
            f"Dia do pagamento (salário de {dinheiro(salario_atual)})",
            salario_atual,
        )
    elif numero == 2:
        valor = max(0, jogador["saldo"] * 0.10)
        jogador["saldo"] -= valor
        jogador["reserva"] = jogador.get("reserva", 0.0) + valor
        registrar(
            nome_jogador,
            f"Início do mês: guardou 10% ({dinheiro(valor)}) na reserva."
        )
    elif numero == 3:
        aplicar_evento(nome_jogador, "Conta de luz", -150)
    elif numero == 4:
        rendimento = max(0, jogador["saldo"]) * 0.01
        aplicar_evento(nome_jogador, "Renda fixa (+1%)", rendimento)
    elif numero == 5:
        aplicar_evento(nome_jogador, "Pagamento das contas", -300)
    elif numero == 6:
        aplicar_evento(nome_jogador, "Consulta e remédios", -200)
    elif numero == 7:
        registrar(nome_jogador, "Jogou novamente: pode girar a roleta mais uma vez.")
        st.info("Jogue novamente: escolha outra casa/evento.")
    elif numero == 8:
        st.session_state["evento_especial"] = 8
        return
    elif numero == 9:
        rendimento = max(0, jogador["saldo"]) * 0.08
        aplicar_evento(nome_jogador, "Investimento em ações (+8%)", rendimento)
    elif numero == 10:
        aplicar_evento(nome_jogador, "Compras inesperadas", -180)
    elif numero == 11:
        aplicar_evento(nome_jogador, "Renda extra", 250)
    elif numero == 12:
        rendimento = max(0, jogador["saldo"]) * 0.01
        aplicar_evento(nome_jogador, "Investimento seguro (+1%)", rendimento)
    elif numero == 13:
        rendimento = max(0, jogador["saldo"]) * 0.015
        aplicar_evento(nome_jogador, "Tesouro Direto (+1,5%)", rendimento)
    elif numero == 14:
          registrar(nome_jogador, "Jogada normal: gire a roleta e siga a instrução sorteada.")
          st.info("Gire a roleta e escolha a casa sorteada.")
    elif numero == 15:
        aplicar_evento(nome_jogador, "Desconto em compras", 100)
    elif numero == 16:
        perda = max(0, jogador["saldo"]) * 0.08
        aplicar_evento(nome_jogador, "Investimento em ações (−8%)", -perda)
    elif numero == 17:
        aplicar_evento(nome_jogador, "Conta de internet", -120)
    elif numero == 18:
        rendimento = max(0, jogador["saldo"]) * 0.01
        aplicar_evento(nome_jogador, "Investimento em CDB (+1%)", rendimento)
    elif numero == 19:
        aplicar_evento(nome_jogador, "Venda de objeto usado", 150)
    elif numero == 20:
        aplicar_evento(nome_jogador, "Férias e passeios", -400)
    elif numero == 21:
        aplicar_evento(nome_jogador, "Compra por impulso", -200)
    elif numero == 22:
        rendimento = max(0, jogador["saldo"]) * 0.10
        aplicar_evento(nome_jogador, "Investimento em ações (+10%)", rendimento)
    elif numero == 23:
        perda = max(0, jogador["saldo"]) * 0.15
        aplicar_evento(nome_jogador, "Queda na bolsa (−15%)", -perda)
    elif numero == 24:
        registrar(nome_jogador, "Jogou novamente: pode girar a roleta mais uma vez.")
        st.info("Jogue novamente: escolha outra casa/evento.")
    elif numero == 25:
        st.session_state["evento_especial"] = 25
        return
    elif numero == 26:
        rendimento = max(0, jogador["saldo"]) * 0.02
        aplicar_evento(nome_jogador, "Fundo imobiliário (+2%)", rendimento)
    elif numero == 27:
        aplicar_evento(nome_jogador, "Emergência médica", -2000)
    elif numero == 28:
        aplicar_evento(nome_jogador, "Juros por atraso", -100)
    elif numero == 29:
        rendimento = max(0, jogador["saldo"]) * 0.005
        aplicar_evento(nome_jogador, "Poupança (+0,5%)", rendimento)
    elif numero == 30:
        if jogador["saldo"] > 0:
            bonus = jogador["saldo"] * 0.05
            aplicar_evento(nome_jogador, "Bônus de fechamento do mês (+5%)", bonus)
        else:
            registrar(nome_jogador, "Fechamento do mês: saldo não positivo, sem bônus.")
    st.session_state["evento_especial"] = None


with tab_eventos:
    # Ações originais do simulador mantidas junto às 30 casas novas.
    st.subheader("Ações extras do simulador original")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("💵 Receber salário do personagem", key=f"salario_original_{nome}", use_container_width=True):
            aplicar_evento(nome, "Salário do personagem recebido", j["salario"])
            st.rerun()
        if st.button("📈 Promoção (+15% no salário)", key=f"promocao_original_{nome}", use_container_width=True):
            aumento = j["salario"] * 0.15
            j["salario"] += aumento
            registrar(nome, f"Promoção: salário aumentou {dinheiro(aumento)} (15%).")
            st.rerun()
    with c2:
        if st.button("📉 Rebaixamento (−15% no salário)", key=f"rebaixamento_original_{nome}", use_container_width=True):
            reducao = j["salario"] * 0.15
            j["salario"] -= reducao
            registrar(nome, f"Rebaixamento: salário diminuiu {dinheiro(reducao)} (15%).")
            st.rerun()
        if st.button("🚑 Acidente (−R$ 600)", key=f"acidente_original_{nome}", use_container_width=True):
            aplicar_evento(nome, "Acidente", -600)
            st.rerun()
    with c3:
        if st.button("🛒 Supermercado (−R$ 250)", key=f"supermercado_original_{nome}", use_container_width=True):
            aplicar_evento(nome, "Compras de supermercado", -250)
            st.rerun()
        if st.button("🧾 Pagar despesas fixas", key=f"despesas_original_{nome}", use_container_width=True):
            total_despesas = sum(p["despesas"].values())
            aplicar_evento(nome, "Despesas fixas mensais", -total_despesas)
            j["meses"] += 1
            st.rerun()

st.divider()
st.subheader("30 casas do tabuleiro")
st.caption("Selecione o número da casa para aplicar o evento ao jogador escolhido.")
casas = [
        f"💵 1. Dia do pagamento (+{dinheiro(j['salario'])})",
        "🏦 2. Economizar 10% do saldo",
        "💡 3. Conta de luz (−R$ 150)",
        "📈 4. Renda fixa (+1%)",
        "🧾 5. Pagar contas (−R$ 300)",
        "💊 6. Doença (−R$ 200)",
        "🎲 7. Jogar novamente",
        "📉 8. Bolsa: +15% ou −10%",
        "📊 9. Ações (+8%)",
        "🛍️ 10. Compras inesperadas (−R$ 180)",
        "💼 11. Renda extra (+R$ 250)",
        "🛡️ 12. Investimento seguro (+1%)",
        "🇧🇷 13. Tesouro Direto (+1,5%)",
        "🎲 14. Jogar normalmente",
        "🏷️ 15. Desconto (+R$ 100)",
        "📉 16. Ações (−8%)",
        "🌐 17. Internet (−R$ 120)",
        "🏦 18. CDB (+1%)",
        "📦 19. Venda de usado (+R$ 150)",
        "🏖️ 20. Férias (−R$ 400)",
        "🛒 21. Compra por impulso (−R$ 200)",
        "📈 22. Ações (+10%)",
        "📉 23. Queda na bolsa (−15%)",
        "🎲 24. Jogar novamente",
        "🎰 25. Aposta: +30% ou −30%",
        "🏢 26. Fundo imobiliário (+2%)",
        "🚑 27. Emergência médica (−R$ 2.000)",
        "⏰ 28. Juros por atraso (−R$ 100)",
        "🐷 29. Poupança (+0,5%)",
        "🏁 30. Fechamento do mês (bônus +5%)",
    ]

    colunas = st.columns(3)
    for idx, descricao in enumerate(casas, start=1):
        with colunas[(idx - 1) % 3]:
            if st.button(
                descricao,
                key=f"casa_{idx}_{nome}",
                use_container_width=True,
            ):
                executar_casa(idx, nome)
                st.rerun()

    evento = st.session_state.get("evento_especial")

    if evento == 8:
        st.warning("Bolsa de valores: escolha o resultado da roleta.")
        col_g, col_p = st.columns(2)

        if col_g.button("📈 Ganhar 15%", key=f"bolsa_ganha_{nome}"):
            aplicar_evento(
                nome,
                "Bolsa de valores (+15%)",
                max(0, j["saldo"]) * 0.15,
            )
            st.session_state["evento_especial"] = None
            st.rerun()

        if col_p.button("📉 Perder 10%", key=f"bolsa_perde_{nome}"):
            aplicar_evento(
                nome,
                "Bolsa de valores (−10%)",
                -max(0, j["saldo"]) * 0.10,
            )
            st.session_state["evento_especial"] = None
            st.rerun()

    elif evento == 25:
        st.warning("Aposta arriscada: escolha o resultado da roleta.")
        col_g, col_p = st.columns(2)

        if col_g.button("🎉 Ganhar 30%", key=f"aposta_ganha_{nome}"):
            aplicar_evento(
                nome,
                "Aposta arriscada (+30%)",
                max(0, j["saldo"]) * 0.30,
            )
            st.session_state["evento_especial"] = None
            st.rerun()

        if col_p.button("💸 Perder 30%", key=f"aposta_perde_{nome}"):
            aplicar_evento(
                nome,
                "Aposta arriscada (−30%)",
                -max(0, j["saldo"]) * 0.30,
            )
            st.session_state["evento_especial"] = None
            st.rerun()

    st.caption(
        "Os rendimentos percentuais são calculados sobre o saldo disponível no momento. "
        "A casa 2 transfere 10% do saldo para uma reserva, sem retirar esse dinheiro do patrimônio."
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
            "Parcela da casa (R$)", min_value=1.0,
            value=float(max(1, round(j["salario"] * 0.10, 2))),
            step=50.0, key=f"parcela_casa_{nome}",
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
            "Parcela do carro (R$)", min_value=1.0,
            value=float(max(1, round(j["salario"] * 0.20, 2))),
            step=50.0, key=f"parcela_carro_{nome}",
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
