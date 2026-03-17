import streamlit as st
import pandas as pd
import io

st.title("Conversor de Reportes Mercado Libre")

uploaded_file = st.file_uploader("Subí tu reporte de ventas (Excel)", type=['xlsx'])

if uploaded_file:
    # 1. Cargamos el Excel completo sin saltar filas primero
    df_crudo = pd.read_excel(uploaded_file)
    
    # 2. Buscamos automáticamente la fila donde está "# de venta"
    # Esto evita que el error de 'skiprows' nos rompa el programa
    start_row = 0
    for i, row in df_crudo.iterrows():
        if "# de venta" in row.values:
            start_row = i + 1 # Encontramos la fila de encabezados
            break
            
    # 3. Volvemos a leer pero desde donde encontramos los datos reales
    df_ml = pd.read_excel(uploaded_file, skiprows=start_row)
    
    # Limpiamos nombres de columnas por las dudas (borra espacios locos)
    df_ml.columns = [str(c).strip() for c in df_ml.columns]

    # Verificamos si ahora sí existe la columna
    if '# de venta' in df_ml.columns:
        filas_finales = []
        # ... acá sigue el resto de tu lógica de cálculo ...
        st.success("¡Columna encontrada!")
        
        # (Aquí va el resto del código que ya tenías para procesar)
        for _, row in df_ml.iterrows():
            if pd.isna(row['# de venta']): continue
            # ... tus cálculos ...
            
    else:
        st.error(f"No encontré la columna '# de venta'. Las columnas detectadas son: {list(df_ml.columns)}")
