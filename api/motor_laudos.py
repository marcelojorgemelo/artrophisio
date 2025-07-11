# -*- coding: utf-8 -*-
import json
from typing import List, Dict
from modelos import Achado

class GeradorDeLaudos:
    def __init__(self, caminho_base_conhecimento: str):
        self.base_conhecimento = self._carregar_base_conhecimento(caminho_base_conhecimento)

    def _carregar_base_conhecimento(self, caminho_json: str) -> Dict:
        try:
            with open(caminho_json, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            return {}

    def get_info_exame(self) -> Dict:
        return {
            "nome_exame": self.base_conhecimento.get("nome_exame", ""),
            "template_tecnica": self.base_conhecimento.get("template_tecnica", "")
        }

    def processar_descricao(self, descricao_medico: str) -> List[Achado]:
        descricao_medico = descricao_medico.lower()
        achados_identificados = []
        for achado_info in self.base_conhecimento.get("achados", []):
            for keyword in achado_info.get("keywords", []):
                if keyword in descricao_medico:
                    novo_achado = Achado(
                        id=achado_info["id"],
                        texto_formal=achado_info["texto_formal"],
                        tipo=achado_info["tipo"],
                        conclusao_resumida=achado_info.get("conclusao_resumida")
                    )
                    achados_identificados.append(novo_achado)
                    break
        return achados_identificados