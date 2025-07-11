# Adicione esta nova importação no topo
from mangum import Mangum

# ... (todo o resto do seu código main.py permanece o mesmo) ...
# ... (a definição do app = FastAPI(), as rotas @app.get, @app.post, etc.) ...


# ADICIONE ESTAS DUAS LINHAS NO FINAL DO ARQUIVO
# Esta linha cria o "handler" que o Netlify (AWS Lambda) usará para chamar nossa aplicação
handler = Mangum(app)
# -*- coding: utf-8 -*-
import io
from datetime import datetime
from fastapi import FastAPI, Request, Form
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates

# Importações da biblioteca DOCX
from docx import Document
from docx.shared import Pt, Inches # Inches é novo para controlar o tamanho da imagem
from docx.enum.text import WD_ALIGN_PARAGRAPH # Novo para centralizar

# Nossas classes e motor
from motor_laudos import GeradorDeLaudos
from modelos import Paciente, Laudo

app = FastAPI(title="API Gerador de Laudos")
templates = Jinja2Templates(directory="templates")

MAPA_DE_EXAMES = {
    "joelho": "joelho.json",
    "abdominal": "abdominal.json"
}

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/gerar-laudo")
async def gerar_laudo_endpoint(
    tipo_exame: str = Form(...),
    nome_paciente: str = Form(...),
    data_nascimento: str = Form(...),
    medico_solicitante: str = Form(...),
    descricao_medico: str = Form(...)
):
    caminho_json = MAPA_DE_EXAMES.get(tipo_exame)
    if not caminho_json:
        return {"error": "Tipo de exame não suportado"}

    motor = GeradorDeLaudos(caminho_base_conhecimento=caminho_json)
    
    info_exame = motor.get_info_exame()
    paciente_obj = Paciente(nome=nome_paciente, data_nascimento=data_nascimento)
    lista_de_achados = motor.processar_descricao(descricao_medico)

    laudo_obj = Laudo(
        paciente=paciente_obj,
        medico_solicitante=medico_solicitante,
        lado_exame="", 
        template_tecnica=info_exame["template_tecnica"]
    )
    for achado in lista_de_achados:
        laudo_obj.adicionar_achado(achado)

    # --- GERAÇÃO DO DOCUMENTO WORD COM LOGO ---
    document = Document()
    
    # 1. ADICIONA O LOGO CENTRALIZADO NO TOPO
    # Adiciona um parágrafo que servirá como "container" para a imagem
    p_logo = document.add_paragraph()
    # Centraliza este parágrafo
    p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    # Adiciona a imagem dentro do parágrafo centralizado
    run = p_logo.add_run()
    run.add_picture('artrofisio.jpg', width=Inches(2.5)) # Ajuste o tamanho conforme necessário

    # Define o estilo da fonte padrão para o resto do documento
    style = document.styles['Normal']
    font = style.font
    font.name = 'Arial'
    font.size = Pt(12)

    # 2. Continua adicionando o resto do conteúdo
    document.add_heading(info_exame.get("nome_exame", "LAUDO DE ULTRASSONOGRAFIA").upper(), level=1)
    
    document.add_paragraph(f"Paciente: {laudo_obj.paciente.nome} (Idade: {laudo_obj.paciente.get_idade()} anos)")
    document.add_paragraph(f"Médico Solicitante: Dr(a). {laudo_obj.medico_solicitante}")
    document.add_paragraph(f"Data do Exame: {datetime.now().strftime('%d de %B de %Y')}")

    document.add_heading('TÉCNICA:', level=2)
    document.add_paragraph(laudo_obj.template_tecnica.format(lado=""))

    document.add_heading('ACHADOS:', level=2)
    texto_achados = "\n".join([f"- {achado.texto_formal}" for achado in laudo_obj.achados])
    document.add_paragraph(texto_achados if laudo_obj.achados else "- Estruturas avaliadas sem alterações ecográficas significativas.")

    document.add_heading('IMPRESSÃO DIAGNÓSTICA:', level=2)
    document.add_paragraph(laudo_obj.gerar_impressao_diagnostica())

    # --- FIM DA GERAÇÃO DO DOCUMENTO ---

    file_stream = io.BytesIO()
    document.save(file_stream)
    file_stream.seek(0)
    
    return StreamingResponse(
        file_stream,
        media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        headers={'Content-Disposition': f'attachment; filename="laudo_{paciente_obj.nome.replace(" ", "_")}.docx"'}
    )