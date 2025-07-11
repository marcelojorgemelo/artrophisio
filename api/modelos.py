# -*- coding: utf-8 -*-
from dataclasses import dataclass, field
from datetime import datetime
from typing import List

@dataclass
class Paciente:
    nome: str
    data_nascimento: str

    def get_idade(self) -> int:
        hoje = datetime.now()
        nascimento = datetime.strptime(self.data_nascimento, "%Y-%m-%d")
        idade = hoje.year - nascimento.year - ((hoje.month, hoje.day) < (nascimento.month, nascimento.day))
        return idade

@dataclass
class Achado:
    id: str
    texto_formal: str
    tipo: str
    conclusao_resumida: str = None

@dataclass
class Laudo:
    paciente: Paciente
    medico_solicitante: str
    lado_exame: str
    template_tecnica: str
    achados: List[Achado] = field(default_factory=list)

    def adicionar_achado(self, achado: Achado):
        self.achados.append(achado)

    def gerar_impressao_diagnostica(self) -> str:
        conclusoes = [achado.conclusao_resumida for achado in self.achados if achado.tipo == 'patologico' and achado.conclusao_resumida]
        if not conclusoes:
            return "Exame ultrassonográfico do joelho dentro dos limites da normalidade."
        return "Impressão: " + ", ".join(c.capitalize() for c in conclusoes) + "."