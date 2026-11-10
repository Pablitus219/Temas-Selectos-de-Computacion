import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Monitor de Portafolio y Riesgo", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    div[data-testid="metric-container"] {
        background-color: #1e1e1e;
        border: 1px solid #333;
        padding: 5% 5% 5% 10%;
        border-radius: 5px;
        color: white;
    }
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. EXTRACCIÓN DE DATOS ---
@st.cache_data
def cargar_datos():
    try:
        conn = sqlite3.connect('portafolio.db')
        df = pd.read_sql_query("SELECT * FROM historico_activos", conn)
        conn.close()
        df['Date'] = pd.to_datetime(df['Date'])
        return df
    except sqlite3.Error as e:
        st.error(f"Error conectando a la base de datos: {e}")
        return pd.DataFrame()

df = cargar_datos()

if df.empty:
    st.error("No se encontraron datos. Asegúrate de ejecutar 'agente_financiero.py' primero.")
else:
    # --- 3. PANEL LATERAL: SIMULADOR DE CARTERA Y CRÉDITOS ---
    st.sidebar.header(" Simulación de Cartera")
    st.sidebar.markdown("Ingresa el peso (%) para cada activo.")
    
    tickers_bd = df['Ticker'].unique().tolist()
    tickers_portafolio = [t for t in tickers_bd if t != 'SPY']
    
    pesos_usuario = {}
    peso_total = 0
    
    # Cambiamos sliders por number_input para ingresar el valor numérico directamente
    for ticker in tickers_portafolio:
        peso_inicial = int(100 / len(tickers_portafolio)) if len(tickers_portafolio) > 0 else 0
        pesos_usuario[ticker] = st.sidebar.number_input(f"Peso {ticker} (%)", min_value=0, max_value=100, value=peso_inicial, step=1)
        peso_total += pesos_usuario[ticker]
        
    if peso_total != 100:
        st.sidebar.warning(f"⚠️ El peso total es {peso_total}%. Ajusta los valores para que sumen exactamente 100%.")
    
    st.sidebar.divider()
    
    # Nuevo filtro de periodos de tiempo con las opciones exactas solicitadas
    periodos_opciones = {
        "1 Mes (30 días)": 30,
        "3 Meses (90 días)": 90,
        "6 Meses (180 días)": 180,
        "Hace exactamente 1 Año": 365,
        "Histórico Máximo Disponible": len(df['Date'].unique())
    }
    
    periodo_seleccionado = st.sidebar.selectbox("Periodo de Análisis", list(periodos_opciones.keys()), index=2)
    dias_historia = periodos_opciones[periodo_seleccionado]

    st.sidebar.divider()
    st.sidebar.subheader("👨‍💻 Equipo de Desarrollo")
    st.sidebar.caption("""
    - Cortes Aceves Joshua Alejandro
    - Cid Ibarra Paulette Aranza
    - Fuentes Guzmán Luisa María
    - Garcia Mercado Karina
    - López Rivera Pablo Alberto
    - Montoya Torres Angeles Helena
    - Pérez Sánchez Anuar Gustavo
    - Yunuen Vélez Barrera
    """)

    # --- 4. PROCESAMIENTO Y CÁLCULOS PONDERADOS ---
    fecha_corte = df['Date'].max() - pd.Timedelta(days=dias_historia)
    df_filtrado = df[df['Date'] >= fecha_corte].copy()
    
    df_filtrado['Retorno_Acumulado_Ind'] = df_filtrado.groupby('Ticker')['Close'].transform(lambda x: (x / x.iloc[0]) * 100)

    if peso_total == 100:
        df_pivot_retornos = df_filtrado.pivot(index='Date', columns='Ticker', values='Retorno_Diario').fillna(0)
        
        if 'SPY' in df_pivot_retornos.columns:
            df_port_calc = df_pivot_retornos.drop(columns=['SPY'])
        else:
            df_port_calc = df_pivot_retornos
            
        pesos_array = np.array([pesos_usuario[t] / 100 for t in df_port_calc.columns])
        retorno_diario_portafolio = df_port_calc.dot(pesos_array)
        rendimiento_acumulado_port = (1 + retorno_diario_portafolio).cumprod() * 100
        
        volatilidad_portafolio = retorno_diario_portafolio.std() * np.sqrt(252) * 100
        rend_total_portafolio = ((rendimiento_acumulado_port.iloc[-1] - 100) / 100) * 100
        
        if 'SPY' in df_pivot_retornos.columns:
            rend_spy_acum = (1 + df_pivot_retornos['SPY']).cumprod() * 100
            rend_total_spy = ((rend_spy_acum.iloc[-1] - 100) / 100) * 100
        else:
            rend_total_spy = 0
            
        # --- 5. TARJETAS KPI (HEADER) ---
        st.title("Monitor de Portafolio y Análisis de Riesgo")
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Rendimiento Portafolio", f"{rend_total_portafolio:.2f}%")
        delta_spy = rend_total_portafolio - rend_total_spy
        col2.metric("vs S&P 500 (Alpha)", f"{rend_total_spy:.2f}%", f"{delta_spy:.2f}% (Diferencia)")
        col3.metric("Volatilidad Anualizada", f"{volatilidad_portafolio:.2f}%", delta_color="inverse")
        
        var_promedio = df_filtrado[df_filtrado['Ticker'] != 'SPY']['VaR_95'].mean() * 100
        col4.metric("VaR Promedio (95%)", f"{var_promedio:.2f}%", "Pérdida esperada", delta_color="inverse")

        st.divider()

        # --- 6. GRÁFICO PRINCIPAL GRANDE ---
        st.subheader("Evolución del Portafolio vs Benchmark")
        fig_port = go.Figure()
        fig_port.add_trace(go.Scatter(x=rendimiento_acumulado_port.index, y=rendimiento_acumulado_port, mode='lines', name='Mi Portafolio', line=dict(color='#00ff00', width=3)))
        
        if 'SPY' in df_pivot_retornos.columns:
            fig_port.add_trace(go.Scatter(x=rend_spy_acum.index, y=rend_spy_acum, mode='lines', name='S&P 500 (SPY)', line=dict(color='#888888', dash='dash')))
        
        fig_port.update_layout(height=500, template="plotly_dark", margin=dict(l=20, r=20, t=30, b=20), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_port, use_container_width=True)

        st.divider()

        # --- 7. GRÁFICOS SECUNDARIOS (Rendimiento Ind, Volatilidad y Volumen) ---
        
        st.subheader("Rendimiento Individual (Base 100)")
        fig_ind = px.line(df_filtrado[df_filtrado['Ticker'] != 'SPY'], x='Date', y='Retorno_Acumulado_Ind', color='Ticker', template="plotly_dark")
        fig_ind.update_layout(height=400, margin=dict(l=10, r=10, t=30, b=10))
        # Cambiar solo la etiqueta visual del eje Y
        fig_ind.update_yaxes(title_text="Rendimiento por Activo")
        st.plotly_chart(fig_ind, use_container_width=True)
        
        st.divider()
            
        st.subheader("Volatilidad a 30 Días (%)")
        df_filtrado['Volatilidad_Visual'] = df_filtrado['Volatilidad_30d'] * 100
        fig_vol = px.line(df_filtrado[df_filtrado['Ticker'] != 'SPY'], x='Date', y='Volatilidad_Visual', color='Ticker', template="plotly_dark")
        fig_vol.update_layout(height=400, margin=dict(l=10, r=10, t=30, b=10))
        # Cambiar solo la etiqueta visual del eje Y
        fig_vol.update_yaxes(title_text="Volatilidad Por Activo")
        st.plotly_chart(fig_vol, use_container_width=True)
        
        st.divider()
            
        st.subheader("Volumen Transaccionado (Último Día)")
        ultima_fecha = df_filtrado['Date'].max()
        df_volumen_ultimo_dia = df_filtrado[(df_filtrado['Ticker'] != 'SPY') & (df_filtrado['Date'] == ultima_fecha)]
        
        fig_volumen = px.bar(df_volumen_ultimo_dia, x='Ticker', y='Volume', color='Ticker', template="plotly_dark")
        fig_volumen.update_layout(height=400, margin=dict(l=10, r=10, t=30, b=10), showlegend=False)
        # Cambiar solo la etiqueta visual del eje Y
        fig_volumen.update_yaxes(title_text="Volumen Diario por activo")
        st.plotly_chart(fig_volumen, use_container_width=True)

        st.divider()
        
        # --- 8. TABLAS DE DATOS ---
        col_tab1, col_tab2 = st.columns([1, 2])
        
        with col_tab1:
            st.subheader("Riesgos del Activo")
            resumen_data = []
            for ticker in tickers_portafolio:
                df_t = df_filtrado[df_filtrado['Ticker'] == ticker].sort_values(by='Date')
                if not df_t.empty:
                    mercado = "MX" if ".MX" in ticker else "US"
                    precio_ini = df_t.iloc[0]['Close']
                    precio_fin = df_t.iloc[-1]['Close']
                    retorno_real = ((precio_fin - precio_ini) / precio_ini) * 100
                    vol = df_t['Retorno_Diario'].std() * np.sqrt(252) * 100
                    
                    resumen_data.append({
                        'Ticker': ticker,
                        'Mercado': mercado,
                        'Rendimiento (%)': retorno_real,
                        'Volatilidad Anual (%)': vol
                    })
                    
            df_resumen = pd.DataFrame(resumen_data).set_index('Ticker')
            
            if not df_resumen.empty:
                styler = df_resumen.style.background_gradient(
                    subset=['Rendimiento (%)'], cmap='RdYlGn', vmin=-20, vmax=20
                ).format({
                    'Rendimiento (%)': '{:.2f}%',
                    'Volatilidad Anual (%)': '{:.2f}%'
                })
                st.dataframe(styler, use_container_width=True)
                
        with col_tab2:
            st.subheader("Datos Detallados (Últimos Movimientos)")
            st.dataframe(df_filtrado.sort_values(by='Date', ascending=False).head(15), use_container_width=True)