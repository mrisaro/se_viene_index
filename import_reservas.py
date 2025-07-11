import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# 1. Cargar la tabla desde la web del BCRA
url = "https://www.bcra.gob.ar/PublicacionesEstadisticas/Principales_variables_datos.asp?serie=246"
resp = requests.get(url)
resp.raise_for_status()

# 2. Extraer tablas
tablas = pd.read_html(resp.text)
# Suponemos que la tabla requerida es la primera
df = tablas[0]

# 3. Limpiar datos
# La tabla tiene columnas: 'Fecha' y 'Valor'
df.columns = ["Fecha", "Reservas_USD"]
df["Fecha"] = pd.to_datetime(df["Fecha"], dayfirst=True, errors="coerce")
# Quitar filas sin fecha
df = df.dropna(subset=["Fecha"])
# Convertir reservas a número (millones USD)
df["Reservas_USD"] = df["Reservas_USD"].astype(str).str.replace(r"[^\d\.-]", "", regex=True).astype(float) * 1e6

# 4. Filtrar últimos 6 meses
hoy = datetime.today()
hace_6m = hoy - timedelta(days=6 * 30)
df_6m = df[df["Fecha"] >= hace_6m].sort_values("Fecha")

# 5. Mostrar resultados por pantalla
print(df_6m)

# 6. Graficar
plt.figure(figsize=(10, 5))
plt.plot(df_6m["Fecha"], df_6m["Reservas_USD"]/1e9, marker='o', linestyle='-')
plt.title("Reservas Internacionales BCRA (últimos ~6 meses)", color='white')
plt.xlabel("Fecha", color='white')
plt.ylabel("Reservas (miles de millones USD)", color='white')
plt.grid(True, linestyle='--', alpha=0.5)
plt.gca().tick_params(colors='white')
plt.gca().set_facecolor('#2b2b2b')
plt.gcf().patch.set_facecolor('#1e1e1e')
plt.tight_layout()
plt.show()
