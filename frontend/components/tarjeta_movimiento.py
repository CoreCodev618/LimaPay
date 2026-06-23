import flet as ft
from frontend.tema.temas import COLOR_ERROR, COLOR_EXITO, obtener_paleta


def crear_fila_historial(item: dict, modo_oscuro: bool) -> ft.Container:
    paleta = obtener_paleta(modo_oscuro)
    es_ingreso = item["monto"] > 0
    color_monto = COLOR_EXITO if es_ingreso else COLOR_ERROR
    icono = ft.Icons.ACCOUNT_BALANCE_WALLET if es_ingreso else ft.Icons.DIRECTIONS_BUS
    color_icono = COLOR_EXITO if es_ingreso else paleta["texto_secundario"]

    return ft.Container(
        padding=14,
        border_radius=14,
        bgcolor=paleta["tarjeta"],
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(spacing=12, controls=[
                    ft.Icon(icono, color=color_icono, size=20),
                    ft.Column(spacing=2, controls=[
                        ft.Text(item["ruta"], size=14, weight=ft.FontWeight.W_600, color=paleta["texto_principal"]),
                        ft.Text(f'{item["origen"]} · {item["fecha_hora"]}', size=11, color=paleta["texto_secundario"]),
                    ]),
                ]),
                ft.Text(f'{"+" if es_ingreso else ""}S/ {abs(item["monto"]):.2f}', size=14, weight=ft.FontWeight.BOLD, color=color_monto),
            ],
        ),
    )
