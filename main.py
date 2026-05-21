import flet as ft
import math

def main(page: ft.Page):
    # --- CONFIGURACIÓN DE LA PÁGINA ---
    page.title = "Simulador de Teoría de Colas - Telecomunicaciones / Banca"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.primary_color = ft.Colors.BLUE_800
    page.scroll = ft.ScrollMode.AUTO
    page.window_width = 500
    page.window_height = 850

    # --- ELEMENTOS INTERACTIVOS (UI) ---
    txt_lambda = ft.TextField(
        label="Tasa de Llegada (λ) [Clientes/Hora]", 
        hint_text="Ej: 51.43",
        keyboard_type=ft.KeyboardType.NUMBER
    )
    
    txt_mu = ft.TextField(
        label="Tasa de Servicio (μ) [Clientes/Hora/Asesor]", 
        hint_text="Ej: 4.5",
        keyboard_type=ft.KeyboardType.NUMBER
    )
    
    txt_servidores = ft.TextField(
        label="Cantidad de Servidores (s) [Solo para M/M/S]", 
        value="1", 
        keyboard_type=ft.KeyboardType.NUMBER
    )

    dropdown_modelo = ft.Dropdown(
        label="Seleccione el Modelo de Análisis",
        options=[
            ft.dropdown.Option("M/M/1"),
            ft.dropdown.Option("M/M/S")
        ],
        value="M/M/1"
    )

    lbl_error = ft.Text(value="", color=ft.Colors.RED_700, weight=ft.FontWeight.BOLD)
    lbl_alerta = ft.Text(value="", weight=ft.FontWeight.W_500)

    val_rho = ft.Text("-", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900)
    val_lq = ft.Text("-", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900)
    val_wq = ft.Text("-", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900)
    val_w = ft.Text("-", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900)
    progress_bar = ft.ProgressBar(value=0, width=400)

    txt_formulas = ft.Markdown("Seleccione el tipo de modelo y presione calcular para visualizar el desglose científico.")

    # --- LÓGICA MATEMÁTICA INTELIGENTE ---
    def calcular_sistema(e):
        try:
            lbl_error.value = ""
            if not txt_lambda.value or not txt_mu.value:
                raise ValueError("Por favor, ingrese Lambda (λ) y Mu (μ).")
            
            lam = float(txt_lambda.value)
            mu = float(txt_mu.value)
            
            if lam <= 0 or mu <= 0:
                raise ValueError("Las tasas deben ser números mayores a cero.")

            # --- MODELO M/M/1 ---
            if dropdown_modelo.value == "M/M/1":
                rho = lam / mu
                if rho >= 1:
                    raise ValueError("Sistema Inestable (λ >= μ). La fila crecerá infinitamente.")
                
                lq = (lam ** 2) / (mu * (mu - lam))
                w = 1 / (mu - lam)
                wq = lq / lam
                
                txt_formulas.value = (
                    "**Ecuaciones M/M/1 utilizadas:**\n"
                    "• Utilización: $ρ = λ / μ$\n"
                    "• Clientes en cola: $L_q = λ² / [μ(μ - λ)]$\n"
                    "• Tiempo en cola: $W_q = L_q / λ$\n"
                    "• Tiempo en sistema: $W = 1 / (μ - λ)$"
                )

            # --- MODELO M/M/S ---
            else:
                if not txt_servidores.value:
                    raise ValueError("Ingrese el número de servidores (s) para el modelo M/M/S.")
                
                s_real = int(txt_servidores.value)
                if s_real <= 1:
                    raise ValueError("Para el modelo M/M/S, los servidores (s) deben ser mayores a 1.")
                
                rho = lam / (s_real * mu)
                if rho >= 1:
                    raise ValueError(f"Sistema Saturado (ρ = {rho:.2f} >= 1). Agregue más servidores.")
                
                suma = 0.0
                for n in range(s_real):
                    suma += (lam / mu) ** n / math.factorial(n)
                
                termino_s = ((lam / mu) ** s_real) / (math.factorial(s_real) * (1 - rho))
                p0 = 1.0 / (suma + termino_s)
                
                numerador_lq = p0 * ((lam / mu) ** s_real) * rho
                denominador_lq = math.factorial(s_real) * ((1 - rho) ** 2)
                lq = numerador_lq / denominador_lq
                
                wq = lq / lam
                w = wq + (1 / mu)
                
                txt_formulas.value = (
                    "**Ecuaciones M/M/S utilizadas:**\n"
                    "• Utilización: $ρ = λ / (s · μ)$\n"
                    "• Probabilidad Vacío ($P_0$): $[\\sum \\frac{(λ/μ)^n}{n!} + \\frac{(λ/μ)^s}{s!(1-ρ)}]^{-1}$\n"
                    "• Clientes en cola ($L_q$): $\\frac{P_0 (λ/μ)^s ρ}{s! (1-ρ)^2}$\n"
                    "• Tiempo en cola: $W_q = L_q / λ$"
                )

            # --- ACTUALIZACIÓN DE INDICADORES ---
            val_rho.value = f"{rho * 100:.1f}%"
            val_lq.value = f"{lq:.2f} usuarios"
            val_wq.value = f"{wq * 60:.2f} min"
            val_w.value = f"{w * 60:.2f} min"
            
            progress_bar.value = min(rho, 1.0)
            
            if rho > 0.88:
                progress_bar.color = ft.Colors.RED_600
                val_rho.color = ft.Colors.RED_600
                lbl_alerta.value = "🚨 CRÍTICO: Canal saturado. Filas largas y tiempos de espera altos."
                lbl_alerta.color = ft.Colors.RED_600
            elif rho >= 0.70:
                progress_bar.color = ft.Colors.GREEN_600
                val_rho.color = ft.Colors.GREEN_600
                lbl_alerta.value = "✅ ÓPTIMO: Excelente balance entre costo de personal y velocidad de atención."
                lbl_alerta.color = ft.Colors.GREEN_600
            elif rho >= 0.45:
                progress_bar.color = ft.Colors.BLUE_600
                val_rho.color = ft.Colors.BLUE_600
                lbl_alerta.value = "⚡ ESTABLE: Operación fluida, pero con ligera capacidad ociosa."
                lbl_alerta.color = ft.Colors.BLUE_600
            else:
                progress_bar.color = ft.Colors.ORANGE_600
                val_rho.color = ft.Colors.ORANGE_600
                lbl_alerta.value = "⚠️ SUBUTILIZADO: Alerta de sobrecosto. Demasiados asesores ociosos para tan poca demanda."
                lbl_alerta.color = ft.Colors.ORANGE_600

        except ValueError as err:
            lbl_error.value = str(err)
            val_rho.value = "-"
            val_lq.value = "-"
            val_wq.value = "-"
            val_w.value = "-"
            progress_bar.value = 0
            lbl_alerta.value = ""
        
        page.update()

    # --- ELEMENTOS INTERNOS DE LA VENTANA EMERGENTE (VISTA DE INFORME) ---
    cont_informe_dinamico = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, height=450)

    dialogo_pdf = ft.AlertDialog(
        title=ft.Row([
            ft.Icon(ft.Icons.PICTURE_AS_PDF, color=ft.Colors.RED_600),
            ft.Text("Vista Previa del Informe Técnico", size=16, weight=ft.FontWeight.BOLD)
        ], alignment=ft.MainAxisAlignment.START),
        content=ft.Container(
            content=cont_informe_dinamico,
            width=400,
            padding=10
        ),
        actions=[
            ft.TextButton("Cerrar Vista", on_click=lambda _: cerrar_informe())
        ],
        actions_alignment=ft.MainAxisAlignment.END
    )

    def cerrar_informe():
        dialogo_pdf.open = False
        page.update()

    # --- FUNCIÓN QUE CONSTRUYE EL DOCUMENTO EN PANTALLA ---
    def mostrar_pdf_emergente(e):
        if val_rho.value == "-":
            page.overlay.append(ft.SnackBar(content=ft.Text("Primero debes calcular métricas válidas."), open=True))
            page.update()
            return

        s_pdf = "1" if dropdown_modelo.value == "M/M/1" else txt_servidores.value

        # Limpiamos contenido previo de la ventana
        cont_informe_dinamico.controls.clear()

        # Recreamos la estructura del PDF de ReportLab usando componentes nativos limpios
        cont_informe_dinamico.controls.extend([
            ft.Container(
                content=ft.Column([
                    ft.Text("INFORME TÉCNICO DE TRÁNSITO Y OPTIMIZACIÓN", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER),
                    ft.Text(f"Modelo evaluado: {dropdown_modelo.value}", size=12, color=ft.Colors.BLUE_100, text_align=ft.TextAlign.CENTER),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor=ft.Colors.BLUE_800,
                padding=12,
                border_radius=5,
                alignment=ft.alignment.center
            ),
            ft.Divider(height=15, thickness=1),
            
            # Tabla de datos estructurada igual que el PDF
            ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Métrica Analizada", weight=ft.FontWeight.BOLD, size=12)),
                    ft.DataColumn(ft.Text("Valor", weight=ft.FontWeight.BOLD, size=12)),
                ],
                rows=[
                    ft.DataRow(cells=[ft.DataCell(ft.Text("Tasa de Llegada (λ)")), ft.DataCell(ft.Text(txt_lambda.value))]),
                    ft.DataRow(cells=[ft.DataCell(ft.Text("Tasa de Servicio (μ)")), ft.DataCell(ft.Text(txt_mu.value))]),
                    ft.DataRow(cells=[ft.DataCell(ft.Text("Servidores Activos (s)")), ft.DataCell(ft.Text(s_pdf))]),
                    ft.DataRow(cells=[ft.DataCell(ft.Text("Ocupación (rho)")), ft.DataCell(ft.Text(val_rho.value))]),
                    ft.DataRow(cells=[ft.DataCell(ft.Text("Usuarios en Cola (Lq)")), ft.DataCell(ft.Text(val_lq.value))]),
                    ft.DataRow(cells=[ft.DataCell(ft.Text("Tiempo en Cola (Wq)")), ft.DataCell(ft.Text(val_wq.value))]),
                    ft.DataRow(cells=[ft.DataCell(ft.Text("Tiempo en Agencia (W)")), ft.DataCell(ft.Text(val_w.value))]),
                ],
                heading_row_color=ft.Colors.BLUE_GREY_100,
                data_row_min_height=30,
                divider_thickness=0.5
            ),
            ft.Divider(height=15, thickness=1),
            
            # Diagnóstico final al pie de página
            ft.Text("Diagnóstico Operativo:", weight=ft.FontWeight.BOLD, size=12, color=ft.Colors.BLUE_GREY_900),
            ft.Container(
                content=ft.Text(lbl_alerta.value, size=12, weight=ft.FontWeight.W_500),
                padding=10,
                bgcolor=ft.Colors.GREY_100,
                border_radius=5,
                border=ft.border.all(0.5, ft.Colors.GREY_400)
            )
        ])

        # Abrimos la ventana de visualización en la interfaz
        dialogo_pdf.open = True
        page.update()

    # Añadimos la ventana emergente al sistema de capas
    page.overlay.append(dialogo_pdf)

    # --- ENSAMBLADO DE LA PANTALLA PRINCIPAL ---
    page.add(
        ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.ANALYTICS, color=ft.Colors.BLUE_800, size=35),
                    ft.Text("SimulX - Colas de Atención", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800)
                ], alignment=ft.MainAxisAlignment.CENTER),
                ft.Text("Monitoreo e Ingeniería de Tránsito de Clientes", size=12, italic=True, color=ft.Colors.GREY_600),
                ft.Divider(height=10, thickness=1.5),

                # SECCIÓN 1: Variables iniciales
                ft.Text("1. Parámetros de Tasas Globales", weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700),
                txt_lambda,
                txt_mu,
                ft.Container(height=5),
                
                # SECCIÓN 2: Bloque de configuración
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("📋 Configuración del Tipo de Sistema", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.BLUE_900),
                            dropdown_modelo,
                            txt_servidores,
                            ft.Text(
                                "Nota: Si seleccionas M/M/1, el sistema calculará usando 1 solo servidor de forma automática.", 
                                size=11, 
                                italic=True, 
                                color=ft.Colors.GREY_700
                            )
                        ], spacing=10), padding=12
                    ),
                    bgcolor=ft.Colors.BLUE_50
                ),
                
                lbl_error,
                ft.Container(height=5),
                
                ft.ElevatedButton(
                    "Calcular Métricas",
                    icon=ft.Icons.PLAY_ARROW_ROUNDED,
                    on_click=calcular_sistema,
                    style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.BLUE_800),
                    width=250
                ),
                ft.Divider(height=20),

                # SECCIÓN 3: Cuadro de Resultados
                ft.Card(
                    content=ft.Container(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Text("📊 Indicadores de Eficiencia Calculados", weight=ft.FontWeight.BOLD, size=15),
                                ft.Divider(height=5),
                                ft.Row([ft.Text("Ocupación del Sistema (ρ):"), val_rho], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                ft.Row([ft.Text("Usuarios esperando en Fila (Lq):"), val_lq], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                ft.Row([ft.Text("Tiempo prom. en Fila (Wq):"), val_wq], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                ft.Row([ft.Text("Tiempo total en Agencia (W):"), val_w], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                ft.Text("Carga de Trabajo:", size=11, color=ft.Colors.GREY_700),
                                progress_bar,
                                lbl_alerta
                            ], spacing=8), padding=15
                        )
                    )
                ),

                # SECCIÓN 4: Sustentación Matemática
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("🔬 Sustentación de Modelamiento Matemático", weight=ft.FontWeight.BOLD, size=14),
                            ft.Divider(height=5),
                            txt_formulas
                        ], spacing=8), padding=15
                    )
                ),
                
                ft.FilledButton(
                    "Visualizar Informe de Resultados",
                    icon=ft.Icons.MAIN_LAUNCH_PUBLIC,
                    on_click=mostrar_pdf_emergente,
                    style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_700),
                    width=280
                )
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
            padding=15
        )
    )

if __name__ == "__main__":
    ft.app(target=main)
