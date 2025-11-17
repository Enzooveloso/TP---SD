from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def gerar_ata_defesa_pdf(banca):
    """
    Gera um PDF simples com os dados principais da banca e monografia.
    Retorna bytes prontos para resposta HTTP.
    """
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    linha = height - 50

    def escrever(texto, y_offset=20, font="Helvetica", size=12):
        nonlocal linha
        p.setFont(font, size)
        p.drawString(40, linha, texto)
        linha -= y_offset

    monografia = banca.monografia
    escrever("ATA DE DEFESA", y_offset=30, font="Helvetica-Bold", size=16)
    escrever(f"Título: {monografia.titulo}")
    escrever(f"Autor: {monografia.aluno}")
    escrever(f"Orientador: {monografia.orientador}")
    if monografia.coorientador:
        escrever(f"Coorientador: {monografia.coorientador}")
    escrever(f"Data da Defesa: {banca.data_defesa.strftime('%d/%m/%Y %H:%M')}")
    escrever(f"Local: {banca.local_defesa}")

    escrever("Avaliadores:", y_offset=18, font="Helvetica-Bold")
    for prof in banca.avaliadores.all():
        escrever(f"- {prof.user.get_full_name() or prof.user.username}")

    escrever(f"Nota Final: {banca.nota_final or 'Pendente'}", y_offset=25, font="Helvetica-Bold")
    escrever(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", y_offset=25, size=10)

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer.read()
