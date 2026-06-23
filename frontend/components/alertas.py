import flet as ft
from frontend.tema.temas import COLOR_ERROR, COLOR_EXITO, COLOR_ADVERTENCIA

_COLORES = {"error": COLOR_ERROR, "exito": COLOR_EXITO, "advertencia": COLOR_ADVERTENCIA}


def mostrar_notificacion(pagina: ft.Page, mensaje: str, es_error: bool = True, tipo: str = None):
    """tipo: 'error' | 'exito' | 'advertencia'. Si no se pasa, se infiere de es_error (compatibilidad)."""
    tipo = tipo or ("error" if es_error else "exito")
    pagina.show_dialog(ft.SnackBar(
        content=ft.Text(mensaje, color="#FFFFFF", weight=ft.FontWeight.W_600),
        bgcolor=_COLORES.get(tipo, COLOR_ERROR),
        duration=3000,
        behavior=ft.SnackBarBehavior.FLOATING,
        margin=20,
    ))
