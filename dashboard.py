import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

# 1. Configuración de la página
st.set_page_config(page_title="Dashboard de Riesgo Financiero", layout="wide")
st.title(" Análisis de Portafolios y Riesgo Financiero (vs S&P 500)")

# 2. Conectar a la base de datos y extraer datos
@st.cache_data
def cargar_datos():
    conn = sqlite3.connect('portafolio.db')
    df = pd.read_sql_query("SELECT * FROM historico_activos", conn)
    conn.close()
    df['Date'] = pd.to_datetime(df['Date'])
    
    # IMPORTANTE: Calcular el rendimiento acumulado (Base 100) para poder comparar peras con peras.
    # Como SPY vale ~$500 y KO ~$60, no podemos compararlos por precio crudo.
    # El rendimiento acumulado nos dice: "Si hubieras invertido $100 en cada uno, ¿cuánto tendrías hoy?"
    df['Rendimiento_Acumulado'] = df.groupby('Ticker')['Close'].transform(lambda x: (x / x.iloc[0]) * 100)
    
    return df

df = cargar_datos()

if df.empty:
    st.error("No se encontraron datos en la base de datos. ¡Ejecuta tu agente primero!")
else:
    # 3. Panel Lateral para Filtros
    st.sidebar.header("Opciones de Filtrado")
    tickers_disponibles = df['Ticker'].unique().tolist()
    ticker_seleccionado = st.sidebar.multiselect("Selecciona los Activos:", tickers_disponibles, default=tickers_disponibles)
    
    df_filtrado = df[df['Ticker'].isin(ticker_seleccionado)]

    # --- CRÉDITOS DEL EQUIPO ---
    st.sidebar.divider() # Línea separadora visual
    st.sidebar.subheader("👨‍💻 Equipo de Desarrollo")
    st.sidebar.caption("""
    **Integrantes:**
    - Cortes Aceves Joshua Alejandro
    - Cid Ibarra Paulette Aranza
    - Fuentes Guzmán Luisa María
    - Garcia Mercado Karina
    - López Rivera Pablo Alberto
    - Montoya Torres Angeles Helena
    - Pérez Sánchez Anuar Gustavo
    - Yunuen Vélez Barrera
    """)

    # 4. Reporte 1: Rendimiento Histórico Comparativo
    st.subheader("Reporte 1: Rendimiento Histórico (Base 100)")
    st.markdown("Compara el crecimiento de los activos como si hubieras invertido 100 dólares al inicio del periodo.")
    
    # AQUI CAMBIAMOS 'Close' POR 'Rendimiento_Acumulado'
    fig_precio = px.line(df_filtrado, x='Date', y='Rendimiento_Acumulado', color='Ticker', title='Crecimiento de la Inversión (Base 100)')
    st.plotly_chart(fig_precio, use_container_width=True)

    # 5. Dividir la pantalla en dos columnas
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Reporte 2: Volatilidad (Riesgo a 30 días)")
        fig_vol = px.line(df_filtrado, x='Date', y='Volatilidad_30d', color='Ticker', title='Volatilidad Anualizada')
        st.plotly_chart(fig_vol, use_container_width=True)

    with col2:
        st.subheader("Reporte 3: Liquidez (Volumen Transaccionado)")
        fig_volumen = px.bar(df_filtrado, x='Date', y='Volume', color='Ticker', title='Volumen Diario', barmode='group')
        st.plotly_chart(fig_volumen, use_container_width=True)

    # 6. Tabla de datos sin procesar
    st.subheader("Datos Detallados (Últimos 5 días)")
    st.dataframe(df_filtrado.sort_values(by='Date', ascending=False).head(15))