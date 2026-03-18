import streamlit as st
import pandas as pd
import io

# Configuración de la página
st.set_page_config(page_title="Conversor de Ventas ML", layout="wide")
st.title("🚀 Conversor de Reportes Mercado Libre")
st.markdown("Subí el Excel que bajás de Mercado Libre para transformarlo al formato de gestión.")

uploaded_file = st.file_uploader("Seleccioná el archivo .xlsx", type=['xlsx'])

if uploaded_file:
    try:
        # 1. ENCONTRAR LA TABLA AUTOMÁTICAMENTE
        # Leemos el Excel sin saltar filas para buscar los encabezados
        df_temp = pd.read_excel(uploaded_file)
        start_row = 0
        for i, row in df_temp.iterrows():
            if "# de venta" in row.values:
                start_row = i + 1
                break
        
        # 2. LEER LA TABLA REAL
        df_ml = pd.read_excel(uploaded_file, skiprows=start_row)
        # Limpiamos espacios en los nombres de las columnas
        df_ml.columns = [str(c).strip() for c in df_ml.columns]

        if '# de venta' in df_ml.columns:
            st.success("¡Tabla detectada correctamente!")
            
            filas_finales = []

            for _, row in df_ml.iterrows():
                # Si no hay número de venta, saltamos la fila
                if pd.isna(row['# de venta']):
                    continue

                id_vta = row['# de venta']
                
                # Convertimos todo a número. Si hay error o está vacío, ponemos 0.
                def limpiar_monto(valor):
                    n = pd.to_numeric(valor, errors='coerce')
                    return abs(float(n)) if pd.notna(n) else 0.0

                for _, row in df_ml.iterrows():
                if pd.isna(row['# de venta']): continue

                # DATOS DE IDENTIFICACIÓN Y TÍTULO
                id_vta = row['# de venta']
                titulo_pub = row.get('Título de la publicación', 'Sin Título') # <-- AQUÍ CAMBIA "MODA" POR EL TÍTULO
                nombre_cliente = row.get('Nombre del comprador', 'S/D')
                dni_cliente = row.get('Documento del comprador', 'S/D')

                # VALORES MONETARIOS
                precio = limpiar_monto(row.get('Ingresos por productos (ARS)', 0))
                comision = limpiar_monto(row.get('Cargo por venta', 0))
                costo_fijo = limpiar_monto(row.get('Costo fijo', 0))
                cuotas = limpiar_monto(row.get('Costo por ofrecer cuotas', 0))
                envio = limpiar_monto(row.get('Costos de envío (ARS)', 0))
                impuestos = limpiar_monto(row.get('Impuestos', 0))
                
                # Los impuestos se pueden sumar aquí si existen en tu reporte
                # Por ahora calculamos el Neto (lo que te queda a vos)
                monto_neto = precio - (comision + costo_fijo + cuotas + envio)
                
                # --- ESTRUCTURA PARA TU EXCEL DE GESTIÓN ---
                
                filas_finales.append({
                    "Categoría/Producto": titulo_pub, 
                    "ID Operación": id_vta, 
                    "Cliente": nombre_cliente,
                    "DNI/CUIT": dni_cliente,
                    "Monto": monto_neto
                })
                
                # Fila 2: Comisiones
                filas_finales.append({
                    "Categoría/Producto": "Comisiones MP", 
                    "ID Operación": "", 
                    "Cliente": "",
                    "DNI/CUIT": "",
                    "Monto": comision + costo_fijo + cuotas
                })
                
                # Fila 3: Impuestos (si existen)
                if impuestos > 0:
                    filas_finales.append({
                        "Categoría/Producto": "Impuestos/Retenciones", 
                        "ID Operación": "", 
                        "Cliente": "",
                        "DNI/CUIT": "",
                        "Monto": impuestos
                    })
                
                # Fila 4: Envío
                filas_finales.append({
                    "Categoría/Producto": "Costo Envío", 
                    "ID Operación": "", 
                    "Cliente": "",
                    "DNI/CUIT": "",
                    "Monto": envio
                })
                
                # Fila separadora
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
                label="📥 Descargar Excel con Títulos",
                data=output.getvalue(),
                file_name="reporte_ventas_titulos.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.error("No se encontró la columna '# de venta'.")

    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")

    except Exception as e:
        st.error(f"Ocurrió un error inesperado: {e}")
