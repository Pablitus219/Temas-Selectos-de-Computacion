import yfinance as yf
import pandas as pd
import numpy as np
import sqlite3
import datetime

# 1. Configuración del Agente y Activos a monitorear
activos = ['NVDA', 'KO', 'SLV','SPY'] # AQUI PONER LOS TICKERS DE LAS ACCIONES A MONITOREAR
db_name = 'portafolio.db'

def calcular_metricas(df):
    """Calcula métricas financieras clave usando pandas"""
    # Manejar posibles errores si la API devuelve columnas con MultiIndex (versiones nuevas de yfinance)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)
        
    df['Retorno_Diario'] = df['Close'].pct_change()
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    # Volatilidad anualizada a 30 días
    df['Volatilidad_30d'] = df['Retorno_Diario'].rolling(window=30).std() * np.sqrt(252)
    # VaR Histórico al 95% (percentil 5 de los retornos) a 100 días
    df['VaR_95'] = df['Retorno_Diario'].rolling(window=100).quantile(0.05)
    
    # Calcular si hay una anomalía en el volumen (Volumen > Media + 2 Desviaciones Estándar)
    vol_mean = df['Volume'].rolling(window=30).mean()
    vol_std = df['Volume'].rolling(window=30).std()
    df['Anomalia_Volumen'] = np.where(df['Volume'] > (vol_mean + 2 * vol_std), 1, 0)
    
    return df.dropna()

def ejecutar_agente():
    print(f"[{datetime.datetime.now()}] Iniciando agente financiero...")
    
    # Conexión a SQLite
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # Crear tabla si no existe (Esquema Relacional Físico)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historico_activos (
            Date TEXT,
            Ticker TEXT,
            Open REAL, High REAL, Low REAL, Close REAL, Volume INTEGER,
            Retorno_Diario REAL, SMA_20 REAL, SMA_50 REAL, 
            Volatilidad_30d REAL, VaR_95 REAL, Anomalia_Volumen INTEGER,
            PRIMARY KEY (Date, Ticker)
        )
    ''')
    
    # 2. Extracción y Transformación
    for ticker in activos:
        print(f"Descargando datos de {ticker}...")
        # Descargamos los últimos 1 años para tener datos suficientes para las medias móviles de 100 días
        df = yf.download(ticker, period="1y", progress=False)
        
        if not df.empty:
            df = calcular_metricas(df)
            df = df.reset_index() # Convertir la fecha de índice a columna
            df['Ticker'] = ticker
            
            # Formatear la fecha como string (YYYY-MM-DD) para SQLite
            df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
            
            # Mantener solo las columnas que necesitamos
            cols = ['Date', 'Ticker', 'Open', 'High', 'Low', 'Close', 'Volume', 
                    'Retorno_Diario', 'SMA_20', 'SMA_50', 'Volatilidad_30d', 'VaR_95', 'Anomalia_Volumen']
            df = df[cols]
            
            # 3. Carga (Ingesta con Upsert para no duplicar)
            # Pandas no soporta INSERT OR IGNORE directo, iteramos o usamos lógica SQL nativa
            for _, row in df.iterrows():
                placeholders = ', '.join(['?'] * len(row))
                columns = ', '.join(row.index)
                sql = f'INSERT OR REPLACE INTO historico_activos ({columns}) VALUES ({placeholders})'
                cursor.execute(sql, tuple(row))
                
    conn.commit()
    conn.close()
    print("Agente ejecutado con éxito. Base de datos actualizada.")

if __name__ == "__main__":
    ejecutar_agente()