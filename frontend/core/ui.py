"""Helpers de UI reutilizados por todas las vistas: campos, botones, tarjetas, layout responsive."""
import flet as ft
from frontend.tema.temas import COLOR_PRIMARIO, COLOR_PRIMARIO_OSCURO


def ancho_responsive(ancho_pagina: float | None, maximo: int = 380, margen: int = 48, minimo: int = 280) -> int:
    if not ancho_pagina:
        return maximo
    return int(max(minimo, min(ancho_pagina - margen, maximo)))


def campo_texto(paleta: dict, label: str, icono=None, **kwargs) -> ft.TextField:
    return ft.TextField(
        label=label,
        prefix_icon=icono,
        filled=True,
        border_radius=12,
        border_color="transparent",
        focused_border_color=COLOR_PRIMARIO,
        bgcolor=paleta["campo"],
        color=paleta["texto_principal"],
        **kwargs,
    )


def boton_primario(texto: str, on_click=None, degradado: bool = True) -> ft.Container:
    contenido = ft.Text(texto, color="#0A0E1A", weight=ft.FontWeight.BOLD)
    estilo = {"gradient": ft.LinearGradient(colors=[COLOR_PRIMARIO, COLOR_PRIMARIO_OSCURO])} if degradado else {"bgcolor": COLOR_PRIMARIO}
    return ft.Container(
        content=contenido,
        border_radius=12,
        padding=15,
        alignment=ft.Alignment.CENTER,
        ink=True,
        on_click=on_click,
        **estilo,
    )


def boton_secundario(texto: str, paleta: dict, on_click=None) -> ft.TextButton:
    return ft.TextButton(texto, style=ft.ButtonStyle(color=paleta["texto_secundario"]), on_click=on_click)


def boton_volver(paleta: dict, datos_pasajero: dict, al_volver_home=None) -> ft.Button:
    return ft.Button(
        content=ft.Text("Volver al inicio", color=paleta["texto_secundario"]),
        on_click=lambda e: al_volver_home(datos_pasajero) if al_volver_home else None,
    )


def en_progreso(boton: ft.Container) -> None:
    """Reemplaza el contenido de un botón por un spinner (estado de carga)."""
    boton.content = ft.ProgressRing(width=18, height=18, color="#0A0E1A", stroke_width=2)


def tarjeta_contenedor(paleta: dict, controles: list, ancho: int = 380, espaciado: int = 16,
                        alineacion_h=ft.CrossAxisAlignment.START) -> ft.Container:
    return ft.Container(
        width=ancho,
        padding=28,
        border_radius=24,
        bgcolor=paleta["tarjeta"],
        content=ft.Column(spacing=espaciado, horizontal_alignment=alineacion_h, controls=controles),
    )


def fondo_pantalla(paleta: dict, contenido, vertical: bool = True, expandir_contenido: bool = False,
                    alineacion=ft.Alignment.CENTER) -> ft.Container:
    """Container raíz con degradado de fondo, usado por todas las vistas."""
    inicio = ft.Alignment.TOP_CENTER if vertical else ft.Alignment.TOP_LEFT
    fin = ft.Alignment.BOTTOM_CENTER if vertical else ft.Alignment.BOTTOM_RIGHT
    return ft.Container(
        expand=True,
        alignment=alineacion,
        padding=20,
        gradient=ft.LinearGradient(begin=inicio, end=fin, colors=[paleta["fondo_inicio"], paleta["fondo_fin"]]),
        content=contenido,
    )


def pantalla_simple(paleta: dict, titulo: str, controles_extra: list, datos_pasajero: dict, al_volver_home=None,
                     subtitulo: str = None) -> ft.Container:
    """Layout compartido por historial/dashboard/recarga-style: título + contenido + botón volver."""
    encabezado = [ft.Text(titulo, size=24, weight=ft.FontWeight.BOLD, color=paleta["texto_principal"])]
    if subtitulo:
        encabezado.append(ft.Text(subtitulo, size=14, color=paleta["texto_secundario"]))
    return ft.Container(
        expand=True,
        padding=20,
        bgcolor=paleta["fondo_inicio"],
        content=ft.Column(controls=[
            *encabezado,
            *controles_extra,
            ft.Container(content=boton_volver(paleta, datos_pasajero, al_volver_home), alignment=ft.Alignment.CENTER),
        ]),
    )


def aplicar_resize(pagina: ft.Page, control, maximo: int = 380, margen: int = 48, minimo: int = 280, attr: str = "width"):
    """Suscribe el resize de la página para ajustar el ancho de `control` dinámicamente."""
    def manejador(e):
        setattr(control, attr, ancho_responsive(pagina.width, maximo, margen, minimo))
        pagina.update()
    pagina.on_resized = manejador
