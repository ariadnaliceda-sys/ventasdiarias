import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Conversor de Ventas ML", layout="wide")
st.title("🚀 Conversor de Reportes Mercado Libre")

uploaded_file = st.file_uploader("Subí el archivo .xlsx de Mercado Libre", type=['xlsx'])

if uploaded_file:
    try:
        df_temp = pd.read_excel(uploaded_file)
        start_row = 0
        for i, row in df_temp.iterrows():
            if "# de venta" in row.values:
                start_row = i + 1
                break
        
        df_ml = pd.read_excel(uploaded_file, skiprows=start_row)
        df_ml.columns = [str(c).strip() for c in df_ml.columns]

        if '# de venta' in df_ml.columns:
            st.success("¡Tabla detectada! Ajustando comisiones y nombres...")
            
            filas_finales = []

            def limpiar_monto(valor):
                n = pd.to_numeric(valor, errors='coerce')
                return abs(float(n)) if pd.notna(n) else 0.0

            for _, row in df_ml.iterrows():
                if pd.isna(row['# de venta']): continue

                # DATOS DE IDENTIFICACIÓN
                id_vta = row['# de venta']
                titulo_pub = row.get('Título de la publicación', 'Sin Título')
                
                # BUSCAMOS EL NOMBRE CON EL ENCABEZADO QUE MENCIONASTE
                nombre_cliente = row.get('Datos personales o de empresa', 'S/D')
                dni_cliente = row.get('Documento del comprador', 'S/D')
                
                # VALORES MONETARIOS
                precio = limpiar_monto(row.get('Ingresos por productos (ARS)', 0))
                cargo_vta = limpiar_monto(row.get('Cargo por venta', 0))
                costo_fijo = limpiar_monto(row.get('Costo fijo', 0))
                cuotas = limpiar_monto(row.get('Costo por ofrecer cuotas', 0))
                envio = limpiar_monto(row.get('Costos de envío (ARS)', 0))
                
                # NUEVA LÓGICA: Sumamos cargo total + envío en una sola categoría
                comision_total = cargo_vta + costo_fijo + cuotas + envio
                
                # Monto Neto
                monto_neto = precio - comision_total
                
                # --- ESTRUCTURA FINAL ---
                # Fila 1: Producto + Cliente
                filas_finales.append({
                    "Categoría/Producto": titulo_pub, 
                    "ID Operación": id_vta, 
                    "Cliente": nombre_cliente,
                    "DNI/CUIT": dni_cliente,
                    "Monto": monto_neto
                })
                
                # Fila 2: Comisiones MP (Incluye el envío sumado)
                filas_finales.append({
                    "Categoría/Producto": "Comisiones MP + Envío", 
                    "ID Operación": "", 
                    "Cliente": "",
                    "DNI/CUIT": "",
                    "Monto": comision_total
                })
                
                # Fila separadora
                filas_finales.append({"Categoría/Producto": "", "ID Operación": "", "Cliente": "", "DNI/CUIT": "", "Monto": None})

            df_final = pd.DataFrame(filas_finales)

            st.subheader("Vista Previa del Excel de Gestión")
            df_display = df_final.copy()
            df_display['Monto'] = df_display['Monto'].apply(
                lambda x: f"$ {x:,.2f}" if pd.notna(x) and x != "" else ""
            )
            st.dataframe(df_display, use_container_width=True)

            output = io.BytesIO()
            with
