from fpdf import FPDF
import os
from datetime import datetime

class BoletaPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Restaurante EL PAPU', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, 'La mejor comida para los admin del discord', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

def generar_boleta(pedido_id, cliente_nombre, fecha, items, total):
    """
    Genera un PDF con el detalle del pedido.
    items: lista de tuplas (nombre_menu, cantidad, precio_unitario, subtotal)
    """
    pdf = BoletaPDF()
    pdf.add_page()
    
    # Información del Cliente y Pedido
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f'Boleta N°: {pedido_id}', 0, 1)
    pdf.cell(0, 10, f'Fecha: {fecha.strftime("%Y-%m-%d %H:%M:%S")}', 0, 1)
    pdf.cell(0, 10, f'Cliente: {cliente_nombre}', 0, 1)
    pdf.ln(10)
    
    # Tabla de Items
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(80, 10, 'Menú', 1)
    pdf.cell(30, 10, 'Cant.', 1, 0, 'C')
    pdf.cell(40, 10, 'Precio Unit.', 1, 0, 'R')
    pdf.cell(40, 10, 'Subtotal', 1, 1, 'R')
    
    pdf.set_font('Arial', '', 12)
    for nombre, cantidad, precio, subtotal in items:
        pdf.cell(80, 10, str(nombre), 1)
        pdf.cell(30, 10, str(cantidad), 1, 0, 'C')
        pdf.cell(40, 10, f"${precio:.2f}", 1, 0, 'R')
        pdf.cell(40, 10, f"${subtotal:.2f}", 1, 1, 'R')
        
    pdf.ln(5)
    
    # Total
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(150, 10, 'Total a Pagar:', 0, 0, 'R')
    pdf.cell(40, 10, f"${total:.2f}", 0, 1, 'R')
    
    # Guardar PDF
    output_dir = "boletas"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    filename = f"boleta_{pedido_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    filepath = os.path.join(output_dir, filename)
    pdf.output(filepath)
    
    return filepath
