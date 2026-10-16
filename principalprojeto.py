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
        "sobra_pdf": 500,
    },
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
