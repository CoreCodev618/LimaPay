import flet as ft
from frontend.tema.temas import COLOR_ERROR

def mostrar_notificacion(pagina: ft.Page, mensaje: str, es_error: bool = True):
    color_fondo = COLOR_ERROR if es_error else "#22E0A6"
    snack = ft.SnackBar(
        content=ft.Text(mensaje, color="#FFFFFF", weight=ft.FontWeight.W_600),
        bgcolor=color_fondo,
        duration=3000,
        behavior=ft.SnackBarBehavior.FLOATING,
        margin=20
    )
import flet as ft
from frontend.tema.temas import COLOR_ERROR

def mostrar_notificacion(pagina: ft.Page, mensaje: str, es_error: bool = True):
    color_fondo = COLOR_ERROR if es_error else "#22E0A6"
    snack = ft.SnackBar(
        content=ft.Text(mensaje, color="#FFFFFF", weight=ft.FontWeight.W_600),
        bgcolor=color_fondo,
        duration=3000,
        behavior=ft.SnackBarBehavior.FLOATING,
        margin=20
    )
    pagina.show_dialog(snack)