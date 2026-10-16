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
