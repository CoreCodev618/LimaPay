"""Paleta de colores y temas de LimaPay (modo claro/oscuro)."""

COLOR_PRIMARIO = "#22E0A6"
COLOR_PRIMARIO_OSCURO = "#0E9E73"
COLOR_ERROR = "#FF5C5C"
COLOR_EXITO = "#22E0A6"
COLOR_ADVERTENCIA = "#FFB020"

_PALETA_OSCURA = {
    "fondo_inicio": "#0A0E1A",
    "fondo_fin": "#10172A",
    "tarjeta": "#161E2E",
    "campo": "#1D2738",
    "texto_principal": "#F5F7FA",
    "texto_secundario": "#8A93A6",
}

_PALETA_CLARA = {
    "fondo_inicio": "#F4F6FA",
    "fondo_fin": "#E8ECF5",
    "tarjeta": "#FFFFFF",
    "campo": "#F0F2F7",
    "texto_principal": "#0A0E1A",
    "texto_secundario": "#5B6477",
}


def obtener_paleta(modo_oscuro: bool) -> dict:
    return _PALETA_OSCURA if modo_oscuro else _PALETA_CLARA
