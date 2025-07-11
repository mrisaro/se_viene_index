import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd
from prettytable import PrettyTable
import random
import os
import matplotlib.image as mpimg
from scipy.interpolate import make_interp_spline

def estimar_dolar():
    # === INPUT USUARIO ===
    print("\n=== DATOS DEL DÓLAR ===")
    try:
        valor_dolar_hoy = float(input("Ingrese el valor actual del dólar (en pesos argentinos): "))
        variacion_porcentual_diaria = float(input("Ingrese la variación porcentual diaria esperada (ej. 0.5 para 0.5%): ")) / 100
    except ValueError:
        print("Error: Ingrese valores válidos.")
        return

    # === RESERVAS REALES DE CSV ===
    try:
        df_reservas = pd.read_csv("reservas_bcra_ultimos3meses.csv", dayfirst=True)
        df_reservas["Fecha"] = pd.to_datetime(df_reservas["Fecha"], dayfirst=True)
        df_reservas["Reservas_USD"] = df_reservas["Reservas_USD"] * 1e9
        df_reservas = df_reservas.sort_values("Fecha")
    except Exception as e:
        print("Error al leer reservas:", e)
        return

    reservas_hoy = df_reservas.iloc[-1]["Reservas_USD"]
    reservas_ayer = df_reservas.iloc[-2]["Reservas_USD"]
    variacion_diaria_reservas = (reservas_hoy - reservas_ayer) / reservas_ayer
    dias_habiles = pd.date_range(start=datetime.now(), end=datetime(2027, 12, 10), freq="B").shape[0]

    valor_dolar_final = valor_dolar_hoy * ((1 + variacion_porcentual_diaria) ** dias_habiles)
    probabilidad = np.mean(variacion_porcentual_diaria * 23.4 + random.uniform(17, 25))

    # === TABLA ===
    tabla = PrettyTable()
    tabla.title = "Proyección Económica Argentina (2023-2027)"
    tabla.field_names = ["Descripción", "Valor"]
    tabla.align["Descripción"] = "l"
    tabla.align["Valor"] = "r"
    tabla.add_row(["Valor actual del dólar", f"${valor_dolar_hoy:,.2f}"])
    tabla.add_row(["Variación diaria dólar", f"{variacion_porcentual_diaria*100:.2f}%"])
    tabla.add_row(["Dólar proyectado (10/12/2027)", f"${valor_dolar_final:,.2f}"])
    tabla.add_row(["Reservas actuales (USD)", f"${reservas_hoy:,.0f}"])
    tabla.add_row(["Días hábiles proyectados", f"{dias_habiles}"])
    print("\n" + "="*80)
    print(tabla)
    print("="*80 + "\n")

    # === GRAFICAR ===
    fig = plt.figure(figsize=(16, 10), facecolor='#1e1e1e')
    gs = fig.add_gridspec(3, 3)

    # --- Gráfico del Dólar (arriba) ---
    fechas = pd.date_range(datetime.now(), periods=dias_habiles, freq="B")
    valores_dolar = [valor_dolar_hoy * ((1 + variacion_porcentual_diaria) ** i) for i in range(dias_habiles)]

    ax1 = fig.add_subplot(gs[0:2, :2])
    ax1.plot(fechas, valores_dolar, color='#C0C0C0', linewidth=2)
    ax1.set_title(f'Proyección del Dólar ({datetime.now().strftime("%d/%m/%Y")} ➜ 10/12/2027)', fontsize=14, color='white')
    ax1.set_ylabel('Pesos Argentinos por Dólar', fontsize=12, color='white')
    ax1.grid(True, linestyle='--', alpha=0.4)
    ax1.tick_params(colors='white')
    ax1.set_facecolor('#2b2b2b')
    plt.setp(ax1.get_xticklabels(), rotation=45, color='white')
    plt.setp(ax1.get_yticklabels(), color='white')

    # --- Gráfico de Reservas (abajo) ---
    ax2 = fig.add_subplot(gs[2, :2])
    ax2.bar(df_reservas["Fecha"], df_reservas["Reservas_USD"]/1e9, color='skyblue', label='Reservas (miles de millones USD)')

    # Spline para tendencia
    #dates_ord = df_reservas["Fecha"].map(datetime.toordinal)
    #xnew = np.linspace(dates_ord.min(), dates_ord.max() + 30, 300)
    #spline = make_interp_spline(dates_ord, df_reservas["Reservas_USD"], k=3)
    #y_smooth = spline(xnew)
    #fechas_spline = [datetime.fromordinal(int(x)) for x in xnew]
    #ax2.plot(fechas_spline, y_smooth / 1e9, color='red', linewidth=2.5, label='Tendencia esperada (Spline)')

    ax2.set_title("Reservas Internacionales Reales", fontsize=14, color='white')
    ax2.set_xlabel('Fecha', fontsize=12, color='white')
    ax2.set_ylabel('Miles de millones de USD', fontsize=12, color='white')
    ax2.grid(True, linestyle='--', alpha=0.4)
    ax2.tick_params(colors='white')
    ax2.set_facecolor('#2b2b2b')
    plt.setp(ax2.get_xticklabels(), rotation=45, color='white')
    plt.setp(ax2.get_yticklabels(), color='white')
    ax2.legend(facecolor='#2b2b2b', edgecolor='white', fontsize=10)

    # --- Panel lateral GSV ---
    ax3 = fig.add_subplot(gs[:, 2])
    ax3.axis('off')
    estado = (
        ("CORRALITO", '#ff3c38') if probabilidad > 60 else
        ("Picadolar", '#ff9800') if probabilidad > 40 else
        ("NPN", '#f4e04d') if probabilidad > 20 else
        ("TMC", '#90ee90')
    )

    ax3.text(0.5, 0.85, "🔮 Probabilidad de GSV", ha='center', fontsize=26, fontweight='bold', color='#87cefa')
    ax3.text(0.5, 0.7, f"{probabilidad:.1f}%", ha='center', fontsize=44, fontweight='bold', color='white')
    ax3.text(0.5, 0.58, "Modelo empírico con datos\nreales del BCRA y doctrina justicialista", 
             ha='center', fontsize=8, color='gray')
    ax3.text(0.5, 0.40, "Estado económico:", ha='center', fontsize=26, color='white')
    ax3.text(0.5, 0.27, estado[0], ha='center', fontsize=44, fontweight='bold', color=estado[1])

    # --- Logo GSV ---
    logo_path = "logo_gsv.png"
    if os.path.exists(logo_path):
        logo = mpimg.imread(logo_path)
        ax_logo = fig.add_axes([0.72, 0.03, 0.2, 0.2], anchor='SE', zorder=1)
        ax_logo.imshow(logo)
        ax_logo.axis('off')

    plt.tight_layout()
    plt.show()

# === EJECUCIÓN ===
estimar_dolar()

