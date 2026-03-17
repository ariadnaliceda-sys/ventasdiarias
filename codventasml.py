import streamlit as st
import pandas as pd
import io

st.title("Conversor de Reportes Mercado Libre")

uploaded_file = st.file_uploader("Subí tu reporte de ventas (Excel)", type=['xlsx'])

if uploaded_file:
    # 1. Leer el Excel saltando las primeras filas (el reporte tiene encabezados arriba)
    # Según la imagen, los encabezados reales parecen estar en la fila 8 o 9
    df_ml = pd.read_excel(uploaded_file, skiprows=8) 
    
    # Limpiamos nombres de columnas (quitar espacios extras)
    df_ml.columns = [str(c).strip() for c in df_ml.columns]

    filas_finales = []

    for _, row in df_ml.iterrows():
        # Saltamos filas vacías si las hay
        if pd.isna(row['# de venta']):
            continue

        # Extraemos y convertimos a número (limpiando posibles errores)
        id_vta = row['# de venta']
        precio = float(row.get('Ingresos por productos (ARS)', 0))
        
        # ML pone cargos en negativo, usamos abs() para tener el valor y luego restar
        comision = abs(float(row.get('Cargo por venta', 0)))
        costo_fijo = abs(float(row.get('Costo fijo', 0)))
        cuotas = abs(float(row.get('Costo por ofrecer cuotas', 0)))
        envio = abs(float(row.get('Costos de envío (ARS)', 0)))
        
        # --- Lógica para tu Excel ---
        # 1. Fila de la Venta (Moda)
        monto_neto = precio - (comision + costo_fijo + cuotas + envio)
        filas_finales.append({
            "Concepto": "Moda", 
            "ID": id_vta, 
            "Monto": monto_neto
        })
        
        # 2. Fila de Comisiones Totales
        filas_finales.append({
            "Concepto": "Comisiones MP", 
            "ID": "", 
            "Monto": comision + costo_fijo + cuotas
        })
        
        # 3. Fila de Envío
        filas_finales.append({
            "Concepto": "Costos Envío", 
            "ID": "", 
            "Monto": envio
        })
        
        # Espacio separador
        filas_finales.append({"Concepto": "", "ID": "", "Monto": ""})

    df_final = pd.DataFrame(filas_finales)
    st.dataframe(df_final)

    # Botón de descarga
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_final.to_excel(writer, index=False)
    
    st.download_button("Descargar Excel Procesado", output.getvalue(), "ventas_contabilidad.xlsx")
