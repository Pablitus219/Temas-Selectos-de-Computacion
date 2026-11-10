# Analizador de Portafolios y Riesgo Financiero

Este proyecto implementa un agente automatizado en Python que extrae datos financieros reales, calcula métricas de riesgo y rendimiento (vs S&P 500), y las visualiza en un Dashboard interactivo.

## Equipo de Desarrollo
* Cortes Aceves Joshua Alejandro
* Cid Ibarra Paulette Aranza
* Fuentes Guzmán Luisa María
* Garcia Mercado Karina
* López Rivera Pablo Alberto
* Montoya Torres Angeles Helena
* Pérez Sánchez Anuar Gustavo
* Yunuen Vélez Barrera

---

## Instrucciones para ejecutar en tu computadora

Sigue estos pasos para correr el proyecto localmente. **Importante:** Asegúrate de abrir tu consola o terminal exactamente en la misma carpeta donde descargaste estos archivos.

### Paso 1: Instalar las dependencias
El proyecto requiere de ciertas librerías de Python para funcionar. Ejecuta el siguiente comando en tu terminal para instalarlas:
```bash
pip install pandas numpy yfinance streamlit plotly
```

### Paso 2: Ejecutar el Agente (Extracción de Datos)
Antes de abrir el dashboard, necesitas que el agente descargue los datos de internet y cree la base de datos. En la misma terminal, ejecuta:
```bash
python agente_financiero.py
```
*(Espera a que la consola te confirme que la base de datos ha sido actualizada).*

### Paso 3: Levantar el Dashboard
Para visualizar los reportes interactivos, ejecuta el siguiente comando en tu terminal:
```bash
streamlit run dashboard.py
```
Esto abrirá automáticamente una ventana en tu navegador web con el Dashboard.

---

## ¿Cómo agregar o quitar acciones (Tickers)?

Si deseas que el agente analice otras empresas o elimine algunas de las actuales, **solo debes modificar un archivo**:

1. Abre el archivo `agente_financiero.py` con cualquier editor de texto.
2. Busca la línea número 8, que se ve así:
   `activos = ['NVDA', 'KO', 'SLV', 'SPY']`
3. Agrega o quita los símbolos que desees entre comillas simples (ej. `'AAPL'` para Apple, `'TSLA'` para Tesla). **No borres `'SPY'`**, ya que se usa para comparar contra el mercado.
4. Guarda el archivo y vuelve a ejecutar el Paso 2 y Paso 3.

---

## Estructura de Archivos y Funciones

Para garantizar el correcto funcionamiento del sistema, respeta la siguiente estructura (se indica qué archivos **NO** debes modificar manualmente):

* **`agente_financiero.py`**: Es el "cerebro" del proyecto. Se conecta a Yahoo Finance, hace los cálculos matemáticos y guarda la información. *(Puedes editarlo solo para cambiar los tickers).*
* **`dashboard.py`**: Lee la base de datos y construye la página web interactiva con las gráficas. **(NO TOCAR)**.
* **`portafolio.db`**: Es la base de datos SQLite creada automáticamente por el agente. **(NO TOCAR ni abrir manualmente)**.
