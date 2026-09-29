"""Automação educacional para cadastro de produtos em um sistema web."""

from getpass import getpass
from pathlib import Path
import time
import webbrowser

import pandas as pd
import pyautogui


URL_SISTEMA = "https://dlp.hashtagtreinamentos.com/python/intensivao/login"
PAUSA_ENTRE_ACOES = 0.5
TEMPO_CARREGAMENTO = 3

# Ajuste estas posições com o auxiliar.py para o seu monitor.
POSICAO_CAMPO_EMAIL = (3315, 408)
POSICAO_CAMPO_CODIGO = (3278, 290)

COLUNAS_OBRIGATORIAS = [
    "codigo",
    "marca",
    "tipo",
    "categoria",
    "preco_unitario",
    "custo",
    "obs",
]


def carregar_produtos(caminho: Path) -> pd.DataFrame:
    """Carrega o CSV e confirma que ele possui as colunas esperadas."""
    tabela = pd.read_csv(caminho)
    colunas_ausentes = [
        coluna for coluna in COLUNAS_OBRIGATORIAS if coluna not in tabela.columns
    ]

    if colunas_ausentes:
        nomes = ", ".join(colunas_ausentes)
        raise ValueError(f"Colunas ausentes no arquivo: {nomes}")

    return tabela


def obter_credenciais() -> tuple[str, str]:
    """Solicita as credenciais sem armazená-las no código-fonte."""
    email = input("E-mail de acesso: ").strip()
    senha = getpass("Senha de acesso: ")

    if not email or not senha:
        raise ValueError("Informe o e-mail e a senha para iniciar a automação.")

    return email, senha


def abrir_sistema() -> None:
    """Abre o sistema de treinamento no navegador padrão."""
    webbrowser.open(URL_SISTEMA)
    time.sleep(TEMPO_CARREGAMENTO)


def fazer_login(email: str, senha: str) -> None:
    """Preenche o formulário de acesso com as credenciais informadas."""
    pyautogui.click(*POSICAO_CAMPO_EMAIL)
    pyautogui.write(email)
    pyautogui.press("tab")
    pyautogui.write(senha)
    pyautogui.press("tab")
    pyautogui.press("enter")
    time.sleep(TEMPO_CARREGAMENTO)


def cadastrar_produto(produto: pd.Series) -> None:
    """Preenche e envia um produto no formulário web."""
    pyautogui.click(*POSICAO_CAMPO_CODIGO)

    for coluna in COLUNAS_OBRIGATORIAS[:-1]:
        pyautogui.write(str(produto[coluna]))
        pyautogui.press("tab")

    observacao = produto["obs"]
    if not pd.isna(observacao):
        pyautogui.write(str(observacao))

    pyautogui.press("tab")
    pyautogui.press("enter")
    pyautogui.scroll(5000)


def executar() -> None:
    """Executa o fluxo completo de login e cadastro."""
    pasta_projeto = Path(__file__).resolve().parent
    arquivo_dados = pasta_projeto / "produtos_exemplo.csv"
    tabela = carregar_produtos(arquivo_dados)
    email, senha = obter_credenciais()

    pyautogui.PAUSE = PAUSA_ENTRE_ACOES
    pyautogui.FAILSAFE = True

    abrir_sistema()
    fazer_login(email, senha)

    total = len(tabela)
    for numero, (_, produto) in enumerate(tabela.iterrows(), start=1):
        cadastrar_produto(produto)
        print(f"Produto {numero}/{total} cadastrado.")

    print("Cadastro concluído.")


if __name__ == "__main__":
    executar()
