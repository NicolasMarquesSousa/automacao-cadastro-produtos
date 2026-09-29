import tempfile
import unittest
from pathlib import Path

from automacao import carregar_produtos


CSV_VALIDO = """codigo,marca,tipo,categoria,preco_unitario,custo,obs
ABC001,Marca Teste,Mouse,1,50.00,20.00,
"""


class CarregarProdutosTest(unittest.TestCase):
    def criar_csv(self, conteudo: str) -> Path:
        arquivo = tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", encoding="utf-8", delete=False
        )
        self.addCleanup(Path(arquivo.name).unlink, missing_ok=True)
        arquivo.write(conteudo)
        arquivo.close()
        return Path(arquivo.name)

    def test_carrega_arquivo_valido(self):
        tabela = carregar_produtos(self.criar_csv(CSV_VALIDO))

        self.assertEqual(len(tabela), 1)
        self.assertEqual(tabela.loc[0, "codigo"], "ABC001")

    def test_rejeita_arquivo_sem_colunas_obrigatorias(self):
        caminho = self.criar_csv("codigo,marca\nABC001,Marca Teste\n")

        with self.assertRaisesRegex(ValueError, "Colunas ausentes"):
            carregar_produtos(caminho)


if __name__ == "__main__":
    unittest.main()
