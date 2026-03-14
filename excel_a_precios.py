"""
TURPICOOL - Descarga Excel de Google Drive y genera precios.json
Este script lo ejecuta GitHub Actions automáticamente cada día.
"""

import requests
import pandas as pd
import json
import io

# ── ID del archivo en Google Drive ─────────────────────────────
DRIVE_FILE_ID = "1RlYJMsZ0uMpEhrOlUG2Y9EF88ZHzR3Sk"
SHEET_NAME    = "Lista de Precios"
OUTPUT_FILE   = "precios.json"
# ───────────────────────────────────────────────────────────────

def descargar_excel():
    url = f"https://docs.google.com/spreadsheets/d/{DRIVE_FILE_ID}/export?format=xlsx"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    print("✅ Excel descargado desde Google Drive")
    return io.BytesIO(response.content)

def generar_precios(excel_bytes):
    df = pd.read_excel(excel_bytes, sheet_name=SHEET_NAME, header=10)
    df.columns = ['_', 'codigo', 'producto', 'cantidad', 'precio_ref', 'precio_bs']

    df = df[
        df['codigo'].notna() &
        (df['codigo'] != 'Código') &
        (df['codigo'] != 'TOTAL')
    ]

    df['precio_ref'] = pd.to_numeric(df['precio_ref'], errors='coerce').round(2)

    precios = {}
    for _, row in df.iterrows():
        codigo = str(row['codigo']).strip()
        precio = row['precio_ref']
        if pd.notna(precio):
            precios[codigo] = precio

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(precios, f, indent=2, ensure_ascii=False)

    print(f"✅ precios.json generado con {len(precios)} productos:")
    for codigo, precio in precios.items():
        print(f"   {codigo}: REF. {precio}")

if __name__ == "__main__":
    excel = descargar_excel()
    generar_precios(excel)
