import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Conversor de Ventas ML", layout="wide")
st.title("🚀 Conversor de Reportes Mercado Libre")

uploaded_file = st.file_uploader("Subí tu reporte de ventas (Excel)", type=['xlsx'])

if uploaded_file:
    # 1. Buscamos dónde empieza la tabla
    df_temp = pd.read_excel(uploaded_file)
    start_row = 0
    for i, row in df_temp.iterrows():
        if "# de venta" in row.values:
            start_row = i + 1
            break
            
    # 2. Leemos la tabla real
    df_ml = pd.read_excel(uploaded_file, skiprows=start_row)
    df_ml.columns = [str(c).strip() for c in df_ml.columns]

    if '# de venta' in df_ml.columns:
        st.success("¡Columna encontrada! Procesando datos...")
        
        filas_finales = []

        for _, row in df_ml.iterrows():
            # Si el ID de venta está vacío, saltamos la fila
            if pd.isna(row['# de venta']):
                continue

            id_vta = row['# de venta']
            precio = float(row.get('Ingresos por productos (ARS)', 0))
            comision = abs(float(row.get('Cargo por venta', 0)))
            costo_fijo = abs(float(row.get('Costo fijo', 0)))
            cuotas = abs(float(row.get('Costo por ofrecer cuotas', 0)))
            envio = abs(float(row.get('Costos de envío (ARS)', 0)))
            
            # Calculamos el NETO (lo que te queda a vos)
            monto_neto = precio - (comision + costo_fijo + cuotas + envio)
            
            # --- Formato igual a tu Imagen 2 ---
            # Fila 1: Producto (Neto)
            filas_finales.append({"Categoría": "Moda", "ID Operación": id_vta, "Monto": monto_neto})
            # Fila 2: Comisiones
            filas_finales.append({"Categoría": "Comisiones MP", "ID Operación": "", "Monto": comision + costo_fijo + cuotas})
            # Fila 3: Envío
            filas_finales.append({"Categoría": "Costo Envío", "ID Operación": "", "Monto": envio})
            # Fila separadora (opcional)
            filas_finales.append({"Categoría": "---", "ID Operación": "", "Monto": ""})

        # 3. Creamos el DataFrame final para mostrar
        df_final = pd.DataFrame(filas_finales)
        
        # Mostramos una tabla linda en Streamlit
        st.subheader("Vista Previa del Excel de Gestión")
        st.dataframe(df_final, use_container_width=True)

        # 4. Botón de Descarga
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_final.to_excel(writer, index=False, sheet_name='Gestión')
        
        st.download_button(
            label="📥 Descargar Excel para mi jefe",
            data=output.getvalue(),
            file_name="reporte_procesado.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.error("No se encontró la columna '# de venta'. Revisá el formato del Excel.")
