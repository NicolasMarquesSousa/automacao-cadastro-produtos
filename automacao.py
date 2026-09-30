"""Automação educacional para cadastro de produtos em um sistema web."""

import argparse
from getpass import getpass
from pathlib import Path
import time
from typing import Any
import webbrowser

import pandas as pd


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
COLUNAS_NAO_VAZIAS = [coluna for coluna in COLUNAS_OBRIGATORIAS if coluna != "obs"]


def carregar_produtos(caminho: Path) -> pd.DataFrame:
    """Carrega o CSV e valida estrutura e campos necessários."""
    tabela = pd.read_csv(caminho, dtype=str, keep_default_na=False)
    tabela.columns = [coluna.strip() for coluna in tabela.columns]
    colunas_ausentes = [
        coluna for coluna in COLUNAS_OBRIGATORIAS if coluna not in tabela.columns
    ]

    if colunas_ausentes:
        nomes = ", ".join(colunas_ausentes)
        raise ValueError(f"Colunas ausentes no arquivo: {nomes}")

    for coluna in COLUNAS_OBRIGATORIAS:
        tabela[coluna] = tabela[coluna].str.strip()

    campos_vazios = tabela[COLUNAS_NAO_VAZIAS].eq("")
    if campos_vazios.any(axis=None):
        problemas = []
        for indice, linha in campos_vazios.iterrows():
            colunas = linha[linha].index.tolist()
            if colunas:
                problemas.append(f"linha {indice + 2}: {', '.join(colunas)}")
        raise ValueError("Campos obrigatórios vazios — " + "; ".join(problemas))

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


def fazer_login(email: str, senha: str, interface: Any) -> None:
    """Preenche o formulário de acesso com as credenciais informadas."""
    interface.click(*POSICAO_CAMPO_EMAIL)
    interface.write(email)
    interface.press("tab")
    interface.write(senha)
    interface.press("tab")
    interface.press("enter")
    time.sleep(TEMPO_CARREGAMENTO)


def cadastrar_produto(produto: pd.Series, interface: Any) -> None:
    """Preenche e envia um produto no formulário web."""
    interface.click(*POSICAO_CAMPO_CODIGO)

    for coluna in COLUNAS_OBRIGATORIAS[:-1]:
        interface.write(str(produto[coluna]))
        interface.press("tab")

    observacao = produto["obs"]
    if observacao:
        interface.write(observacao)

    interface.press("tab")
    interface.press("enter")
    interface.scroll(5000)


def executar(caminho: Path, validar_apenas: bool = False) -> None:
    """Executa o fluxo completo de login e cadastro."""
    tabela = carregar_produtos(caminho)

    if validar_apenas:
        print(f"Base válida: {len(tabela)} produto(s) pronto(s) para cadastro.")
        return

    import pyautogui

    email, senha = obter_credenciais()

    pyautogui.PAUSE = PAUSA_ENTRE_ACOES
    pyautogui.FAILSAFE = True

    abrir_sistema()
    fazer_login(email, senha, pyautogui)

    total = len(tabela)
    for numero, (_, produto) in enumerate(tabela.iterrows(), start=1):
        cadastrar_produto(produto, pyautogui)
        print(f"Produto {numero}/{total} cadastrado.")

    print("Cadastro concluído.")


def criar_parser() -> argparse.ArgumentParser:
    """Configura os argumentos da linha de comando."""
    pasta_projeto = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(
        description="Valida uma base CSV e automatiza o cadastro de produtos."
    )
    parser.add_argument(
        "--arquivo",
        type=Path,
        default=pasta_projeto / "produtos_exemplo.csv",
        help="caminho do CSV de produtos",
    )
    parser.add_argument(
        "--validar-apenas",
        action="store_true",
        help="valida o CSV sem abrir o navegador nem preencher formulários",
    )
    return parser


if __name__ == "__main__":
    argumentos = criar_parser().parse_args()
    executar(argumentos.arquivo, argumentos.validar_apenas)
