# -*- coding: utf-8 -*-
import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "Wells_Revisor" / "wells_blindagem.py"
SPEC = importlib.util.spec_from_file_location("wells_blindagem", MODULE_PATH)
wb = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(wb)


class BlindagemTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "blindagem.txt"

    def tearDown(self):
        self.temp.cleanup()

    def test_arquivo_inexistente_equivale_a_listas_vazias(self):
        data = wb.carregar_listas(self.path)
        self.assertEqual(data[wb.LISTA_BLINDADOS], [])
        self.assertEqual(data[wb.LISTA_TRADUZIVEIS], [])
        self.assertFalse(self.path.exists())

    def test_adicionar_persiste_fisicamente(self):
        wb.adicionar_termo(self.path, wb.LISTA_BLINDADOS, "Dalen")
        wb.adicionar_termo(self.path, wb.LISTA_TRADUZIVEIS, "Queen")
        self.assertTrue(self.path.exists())
        data = wb.carregar_listas(self.path)
        self.assertEqual(data[wb.LISTA_BLINDADOS], ["Dalen"])
        self.assertEqual(data[wb.LISTA_TRADUZIVEIS], ["Queen"])

    def test_editar_corrige_entrada_existente(self):
        wb.adicionar_termo(self.path, wb.LISTA_BLINDADOS, "Dallen")
        wb.editar_termo(self.path, wb.LISTA_BLINDADOS, "Dallen", "Dalen")
        self.assertEqual(
            wb.carregar_listas(self.path)[wb.LISTA_BLINDADOS], ["Dalen"]
        )

    def test_excluir_remove_entrada(self):
        wb.adicionar_termo(self.path, wb.LISTA_BLINDADOS, "Gaius")
        removed = wb.excluir_termo(self.path, wb.LISTA_BLINDADOS, "Gaius")
        self.assertEqual(removed, "Gaius")
        self.assertEqual(wb.carregar_listas(self.path)[wb.LISTA_BLINDADOS], [])

    def test_duplicata_na_mesma_lista_e_rejeitada_sem_diferenciar_caixa(self):
        wb.adicionar_termo(self.path, wb.LISTA_BLINDADOS, "Dalen")
        with self.assertRaises(ValueError):
            wb.adicionar_termo(self.path, wb.LISTA_BLINDADOS, "dalen")

    def test_termo_pode_existir_sem_aparecer_em_documento(self):
        wb.adicionar_termo(self.path, wb.LISTA_BLINDADOS, "NomeQueNaoEstaNoDocumento")
        self.assertEqual(
            wb.carregar_listas(self.path)[wb.LISTA_BLINDADOS],
            ["NomeQueNaoEstaNoDocumento"],
        )

    def test_conflito_entre_listas_e_detectado_sem_resolucao_automatica(self):
        wb.adicionar_termo(self.path, wb.LISTA_BLINDADOS, "Dalen")
        wb.adicionar_termo(self.path, wb.LISTA_TRADUZIVEIS, "dalen")
        data = wb.carregar_listas(self.path)
        self.assertEqual(wb.conflitos(data), ["Dalen"])
        self.assertEqual(data[wb.LISTA_BLINDADOS], ["Dalen"])
        self.assertEqual(data[wb.LISTA_TRADUZIVEIS], ["dalen"])

    def test_entrada_vazia_e_rejeitada(self):
        with self.assertRaises(ValueError):
            wb.adicionar_termo(self.path, wb.LISTA_BLINDADOS, "   ")


if __name__ == "__main__":
    unittest.main()
