import streamlit as st
import pandas as pd
import io

# Configuración de la página
st.set_page_config(page_title="Conversor de Ventas ML", layout="wide")
st.title("🚀 Conversor de Reportes Mercado Libre")

uploaded_file = st.file_uploader("Subí el archivo .xlsx de Mercado Libre", type=['xlsx'])

if uploaded_file:
    try:
        # 1. BUSCAR LA TABLA REAL AUTOMÁTICAMENTE
        df_temp = pd.read_excel(uploaded_file)
        start_row = 0
        for i, row in df_temp.iterrows():
            if "# de venta" in row.values:
                start_row = i + 1
                break
        
        # 2. LEER LA TABLA DESDE LA FILA DETECTADA
        df_ml = pd.read_excel(uploaded_file, skiprows=start_row)
        df_ml.columns = [str(c).strip() for c in df_ml.columns]

        if '# de venta' in df_ml.columns:
            st.success("¡Tabla detectada! Procesando ventas...")
            
            filas_finales = []

            def limpiar_monto(valor):
                n = pd.to_numeric(valor, errors='coerce')
                # Usamos abs() porque ML pone los cargos en negativo
                return abs(float(n)) if pd.notna(n) else 0.0

            for _, row in df_ml.iterrows():
                if pd.isna(row['# de venta']):
                    continue

                # DATOS DE IDENTIFICACIÓN
                id_vta = row['# de venta']
                titulo_pub = row.get('Título de la publicación', 'Sin Título')
                nombre_cliente = row.get('Nombre del comprador', 'S/D')
                dni_cliente = row.get('Documento del comprador', 'S/D')
                
                # VALORES MONETARIOS (Basados en las columnas de tu imagen)
                precio = limpiar_monto(row.get('Ingresos por productos (ARS)', 0))
                cargo_vta = limpiar_monto(row.get('Cargo por venta', 0))
                costo_fijo = limpiar_monto(row.get('Costo fijo', 0))
                cuotas = limpiar_monto(row.get('Costo por ofrecer cuotas', 0))
                envio = limpiar_monto(row.get('Costos de envío (ARS)', 0))
                
                # Sumamos todas las comisiones en una sola variable
                total_comisiones = cargo_vta + costo_fijo + cuotas
                
                # Cálculo del Neto (Lo que te queda a vos)
                # Restamos comisiones y envío del precio total
                monto_neto = precio - (total_comisiones + envio)
                
                # --- ESTRUCTURA PARA TU EXCEL DE GESTIÓN ---
                
                # Fila 1: Título de la publicación + Datos del cliente
                filas_finales.append({
                    "Categoría/Producto": titulo_pub, 
                    "ID Operación": id_vta, 
                    "Cliente": nombre_cliente,
                    "DNI/CUIT": dni_cliente,
                    "Monto": monto_neto
                })
                
                # Fila 2: Comisiones (Cargo vta + Fijo + Cuotas)
                filas_finales.append({
                    "Categoría/Producto": "Comisiones MP", 
                    "ID Operación": "", 
                    "Cliente": "",
                    "DNI/CUIT": "",
                    "Monto": total_comisiones
                })
                
                # Fila 3: Envío (Aparte, como en tu imagen original)
                filas_finales.append({
                    "Categoría/Producto": "Costo Envío", 
                    "ID Operación": "", 
                    "Cliente": "",
                    "DNI/CUIT": "",
                    "Monto": envio
                })
                
                # Fila separadora vacía
                filas_finales.append({"Categoría/Producto": "", "ID Operación": "", "Cliente": "", "DNI/CUIT": "", "Monto": None})

            # 3. CREAR DATAFRAME FINAL
            df_final = pd.DataFrame(filas_finales)

            # 4. VISTA PREVIA
            st.subheader("Vista Previa del Excel de Gestión")
            df_display = df_final.copy()
            df_display['Monto'] = df_display['Monto'].apply(
                lambda x: f"$ {x:,.2f}" if pd.notna(x) and x != "" else ""
            )
            st.dataframe(df_display, use_container_width=True)

            # 5. BOTÓN DE DESCARGA
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_final.to_excel(writer, index=False, sheet_name='Gestión_Ventas')
            
            st.download_button(
                label="📥 Descargar Excel de Gestión",
                data=output.getvalue(),
                file_name="gestion_ventas_ml.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.error("No encontré la columna '# de venta'.")

    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
