import flet as ft

def iniciar_sesion(dni: str, password: str) -> dict:
    # Simulamos el retorno de éxito definido en el documento
    return {"status": True, "pasajero_id": 1, "billetera_id": 100, "nombre": "Sebastian"}

def vista_login():
    titulo = ft.Text("LimaPay", size=40, weight="bold", color="blue")
    txt_dni = ft.TextField(label="DNI", width=300, max_length=8)
    txt_clave = ft.TextField(label="Contraseña", width=300, password=True, can_reveal_password=True)

    
    def autenticar_login(e):
        dni_ingresado = txt_dni.value
        pass_ingresado = txt_clave.value
        resultado = iniciar_sesion(dni = dni_ingresado, password = pass_ingresado)
        
        if resultado['status']:
            print("exito")
        else:
            print("fallo")
    
    btn_ingresar = ft.Button(content=ft.Text("Ingresar"), width=300, on_click=autenticar_login)
    return ft.Column(
        controls = [titulo,txt_dni,txt_clave,btn_ingresar],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )