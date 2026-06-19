
COLOR_PRIMARIO = "#22D3EE"
COLOR_PRIMARIO_OSCURO = "#2563EB"
COLOR_ERROR = "#FF5C7A"
COLOR_EXITO = "#22E0A6"

PALETA_OSCURA = {
    "fondo_inicio": "#0A0E1A",
    "fondo_fin": "#0D1326",
    "tarjeta": "#141B2E",
    "campo": "#1B2440",
    "texto_principal": "#F4F6FB",
    "texto_secundario": "#8A93B0",
}

PALETA_CLARA = {
    "fondo_inicio": "#EAF2FB",
    "fondo_fin": "#FFFFFF",
    "tarjeta": "#FFFFFF",
    "campo": "#F0F4FA",
    "texto_principal": "#101522",
    "texto_secundario": "#5C6680",
}


def obtener_paleta(modo_oscuro: bool) -> dict:
    return PALETA_OSCURA if modo_oscuro else PALETA_CLARA