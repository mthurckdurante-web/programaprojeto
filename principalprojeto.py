nome = st.selectbox(
    "Escolha o jogador",
    list(PERSONAGENS.keys())
)

p = PERSONAGENS[nome]

st.write(
    f"**Classe {p['classe']}** · "
    f"{p['profissao']} · {p['estado_civil']}"
)
m1, m2, m3, m4 = st.columns(4)
m1.metric("Salário atual", dinheiro(j["salario"]))
m2.metric("Saldo disponível", dinheiro(j["saldo"]))
m3.metric("Patrimônio atual", dinheiro(patrimonio(nome)))
m4.metric("Aumento do patrimônio", f"{variacao(nome):.2f}%".replace(".", ","))

tab_eventos, tab_bens, tab_despesas, tab_historico = st.tabs(
    ["🎲 Eventos e ações", "🏠 Casa e carro", "🧾 Despesas mensais", "📜 Histórico"]
)

with tab_eventos:
    st.subheader("Ações do tabuleiro")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("💵 Receber salário", use_container_width=True):
            aplicar(nome, "Salário recebido", j["salario"])
            st.rerun()
        if st.button("📈 Foi promovido (+15%)", use_container_width=True):
            aumento = j["salario"] * 0.15
            j["salario"] += aumento
            registrar(nome, f"Promoção: salário aumentou {dinheiro(aumento)} (15%)")
            st.rerun()
    with c2:
        if st.button("📉 Foi rebaixado (−15%)", use_container_width=True):
            reducao = j["salario"] * 0.15
            j["salario"] -= reducao
            registrar(nome, f"Rebaixamento: salário diminuiu {dinheiro(reducao)} (15%)")
            st.rerun()
        if st.button("🚑 Sofreu acidente (−R$ 600)", use_container_width=True):
            aplicar(nome, "Acidente", -600)
            st.rerun()
    with c3:
        if st.button("🛒 Compras de supermercado (−R$ 250)", use_container_width=True):
            aplicar(nome, "Compras de supermercado", -250)
            st.rerun()
        if st.button("🧾 Pagar despesas fixas do mês", use_container_width=True):
            total = sum(p["despesas"].values())
            aplicar(nome, "Despesas fixas mensais", -total)
            j["meses"] += 1
            st.rerun()
    st.caption("O botão de despesas fixas desconta os valores listados no perfil do personagem. O supermercado de R$ 250 é um evento separado.")

with tab_bens:
    st.subheader("Compra e amortização de bens")
    casa_preco = j["salario"] * 35
    carro_preco = j["salario"] * 4
    a, b = st.columns(2)
    with a:
        st.markdown("### 🏠 Casa")
        st.write(f"Preço da casa (3.500% do salário atual): **{dinheiro(casa_preco)}**")
        st.write(f"Valor da casa adquirido: {dinheiro(j['casa'])}")
        st.write(f"Dívida restante: {dinheiro(j['divida_casa'])}")
        parcela_casa = st.number_input(
            "Valor da parcela da casa (R$)", min_value=1.0,
            value=float(max(1, round(j["salario"] * 0.10, 2))), step=50.0, key=f"parcela_casa_{nome}"
        )
        if st.button("Comprar casa", key=f"comprar_casa_{nome}", use_container_width=True):
            if j["divida_casa"] == 0 and j["casa"] == 0:
                j["divida_casa"] = casa_preco
                j["casa"] = casa_preco
                registrar(nome, f"Comprou uma casa de {dinheiro(casa_preco)} financiada.")
            else:
                st.warning("Este jogador já possui uma casa ou financiamento de casa.")
            st.rerun()
        if st.button("Pagar parcela da casa", key=f"pagar_casa_{nome}", use_container_width=True):
            if j["divida_casa"] <= 0:
                st.warning("Este jogador não tem dívida de casa.")
            elif j["saldo"] < parcela_casa:
                st.error("Saldo insuficiente para pagar essa parcela.")
            else:
                paga = min(parcela_casa, j["divida_casa"])
                j["saldo"] -= paga
                j["divida_casa"] -= paga
                registrar(nome, f"Amortização da casa: pagou {dinheiro(paga)}.")
            st.rerun()
    with b:
        st.markdown("### 🚗 Carro")
        st.write(f"Preço do carro (400% do salário atual): **{dinheiro(carro_preco)}**")
        st.write(f"Valor do carro adquirido: {dinheiro(j['carro'])}")
        st.write(f"Dívida restante: {dinheiro(j['divida_carro'])}")
        parcela_carro = st.number_input(
            "Valor da parcela do carro (R$)", min_value=1.0,
            value=float(max(1, round(j["salario"] * 0.20, 2))), step=50.0, key=f"parcela_carro_{nome}"
        )
        if st.button("Comprar carro", key=f"comprar_carro_{nome}", use_container_width=True):
            if j["divida_carro"] == 0 and j["carro"] == 0:
                j["divida_carro"] = carro_preco
                j["carro"] = carro_preco
                registrar(nome, f"Comprou um carro de {dinheiro(carro_preco)} financiado.")
            else:
                st.warning("Este jogador já possui um carro ou financiamento de carro.")
            st.rerun()
        if st.button("Pagar parcela do carro", key=f"pagar_carro_{nome}", use_container_width=True):
            if j["divida_carro"] <= 0:
                st.warning("Este jogador não tem dívida de carro.")
            elif j["saldo"] < parcela_carro:
                st.error("Saldo insuficiente para pagar essa parcela.")
            else:
                paga = min(parcela_carro, j["divida_carro"])
                j["saldo"] -= paga
                j["divida_carro"] -= paga
                registrar(nome, f"Amortização do carro: pagou {dinheiro(paga)}.")
            st.rerun()

with tab_despesas:
    st.subheader("Despesas registradas no perfil")
    despesas = pd.DataFrame(
        [{"Despesa": k, "Valor mensal": dinheiro(v)} for k, v in p["despesas"].items()]
    )
    st.dataframe(despesas, use_container_width=True, hide_index=True)
    st.write(f"**Total de despesas fixas cadastradas:** {dinheiro(sum(p['despesas'].values()))}")
    st.write(f"**Sobra mensal indicada no PDF:** {dinheiro(p['sobra_pdf'])}")
    st.caption("A sobra indicada no PDF é exibida como referência; o simulador desconta as despesas listadas quando você clica em “Pagar despesas fixas do mês”.")

with tab_historico:
    st.subheader("Histórico de ações")
    if j["historico"]:
        for item in j["historico"]:
            st.write(f"• {item}")
    else:
        st.info("Nenhuma ação registrada.")

st.divider()
if st.button("🔄 Reiniciar partida inteira", type="secondary"):
    del st.session_state["jogadores"]
    st.rerun()
