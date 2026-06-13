import flet as ft

def iniciar_sesion(dni: str, password: str) -> dict:
    # Simulamos el retorno de éxito definido en el documento
    return {"status": True, "pasajero_id": 1, "billetera_id": 100, "nombre": "Sebastian"}

def vista_login():
    # 1. Paleta de colores
    color_primario = "#0056D2"
    color_tarjeta = "#C3E6FF"
    fuente_titulo = "https://fonts.gstatic.com/s/opensans/v40/memvYaGs126MiZpBA-UvWbX2vVnXBbObj2OVTSKmu1aB.woff2"
    
    titulo = ft.Text("LimaPay", size=40, weight="bold", color=color_primario, font_family= fuente_titulo)
    subtitulo = ft.Text("Tu billetera de movilidad", size=14, color=ft.Colors.GREY_700)
    
    txt_dni = ft.TextField(label="DNI", width=280, max_length=8, border_radius=10, prefix_icon=ft.Icons.BADGE, color=ft.Colors.BLACK_87, bgcolor=ft.Colors.WHITE)
    txt_clave = ft.TextField(label="Contraseña", width=280, password=True, can_reveal_password=True, border_radius=10, prefix_icon=ft.Icons.LOCK, color=ft.Colors.BLACK_87, bgcolor=ft.Colors.WHITE)

    
    def autenticar_login(e):
        dni_ingresado = txt_dni.value
        pass_ingresado = txt_clave.value
        resultado = iniciar_sesion(dni = dni_ingresado, password = pass_ingresado)
        
        if resultado['status']:
            print("exito")
        else:
            print("fallo")
    
    btn_ingresar = ft.Button(
        content=ft.Text("Ingresar"), 
        width=280,
        height=50,
        bgcolor=color_primario,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        on_click=autenticar_login
        )
    
    tarjeta_login= ft.Container(
        content = ft.Column(
        controls = [titulo, subtitulo, ft.Divider(height=15, color="transparent"),txt_dni,txt_clave,btn_ingresar],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10
    ),
        bgcolor=color_tarjeta,
        padding=40,
        shadow=ft.BoxShadow(spread_radius=1, blur_radius=20, color= ft.Colors.BLUE_GREY)
    )
    
    return ft.Container(
        content=tarjeta_login,
        alignment=ft.Alignment.CENTER,
        expand= True,
    )