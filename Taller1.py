import os
import streamlit as st
import pandas as pd
import polars as pl
import matplotlib.pyplot as plt
import plotly.express as px

# Obtener el directorio del archivo .py actual y construir la ruta completa al CSV
current_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(current_dir, "depositos_oinks.csv")

# Leer los datos desde el CSV
datos = pl.read_csv(csv_path)

# Usuarios únicos por ubicación
usuarios_por_lugar = datos.group_by("maplocation_name").agg(
    pl.col("user_id").n_unique().alias("cantidad_usuarios")
).sort("cantidad_usuarios", descending=True)

fig1, ax1 = plt.subplots()
bars1 = ax1.bar(usuarios_por_lugar["maplocation_name"].to_list(), usuarios_por_lugar["cantidad_usuarios"].to_list())
ax1.set_xlabel("Ubicación")
ax1.set_ylabel("Cantidad de usuarios únicos")
ax1.set_title("Usuarios únicos por ubicación")
plt.xticks(rotation=20)

# Anotar cada barra con su valor exacto
for bar in bars1:
    height = bar.get_height()
    ax1.annotate(f'{height:.0f}',
                 xy=(bar.get_x() + bar.get_width() / 2, height),
                 xytext=(0, 3), textcoords="offset points",
                 ha='center', va='bottom')

st.pyplot(fig1)
st.write("Segun la gráfica 1, se puede obesevar que CC Los molinos es el punto con mayor cantidad de usuarios de todas las sucursales")

# Valor total de operación por ubicación COP
operacion_t_lugar = datos.group_by("maplocation_name").agg(
    pl.col("operation_value").sum().alias("valor_t_operacion")
).sort("valor_t_operacion", descending=True)

fig2, ax2 = plt.subplots(figsize=(10, 6))
bars2 = ax2.bar(operacion_t_lugar["maplocation_name"].to_list(), operacion_t_lugar["valor_t_operacion"].to_list(), color='purple')
ax2.set_xlabel("Ubicación")
ax2.set_ylabel("Valor total de operación")
ax2.set_title("Valor total de operación por ubicación")
plt.xticks(rotation=20)

# Anotar cada barra con el valor exacto en COP
for bar in bars2:
    height = bar.get_height()
    ax2.annotate(f'COP ${height:,.0f}',
                 xy=(bar.get_x() + bar.get_width() / 2, height),
                 xytext=(0, 3), textcoords="offset points",
                 ha='center', va='bottom')

st.pyplot(fig2)
st.write("Gracias a la segunda grafica se puede concluir que apesar de ser la segunda sucursal en cuanto a cantidad de usuarios se refiere, plaza de las americas es la sucucrsal que posee la mayor cantidad de dinero en la totalidad de transacciones.")

#Puntos con mayor cantidad de operaciones en el día de mayor actividad y su distribución temporal

# Convertir la columna de fecha a datetime
datos = datos.with_columns(
    pl.col("operation_date").str.strptime(pl.Datetime, format="%Y-%m-%d %H:%M:%S")
)

# Extraer solo la fecha (sin la hora) para identificar el día
datos = datos.with_columns(
    pl.col("operation_date").dt.strftime("%Y-%m-%d").alias("op_date_only")
)

# Determinar el día con mayor cantidad de operaciones
day_counts = datos.group_by("op_date_only").agg(
    pl.count("user_id").alias("n_operations")
)
max_day = day_counts.sort("n_operations", descending=True).select("op_date_only").to_series()[0]

# Filtrar los datos para el día de mayor actividad
datos_busiest = datos.filter(pl.col("op_date_only") == max_day)

# Agrupar por ubicación en ese día y contar operaciones
operaciones_por_punto = datos_busiest.group_by("maplocation_name").agg(
    pl.count("user_id").alias("n_operations")
).sort("n_operations", descending=True)

# Seleccionar los 3 puntos con mayor cantidad de operaciones
top_puntos = operaciones_por_punto.head(3)

#Barra de los 10 puntos con mayor operaciones en el día de mayor actividad
fig3, ax3 = plt.subplots(figsize=(10, 6))
bars3 = ax3.bar(top_puntos["maplocation_name"].to_list(), top_puntos["n_operations"].to_list(), color='orange')
ax3.set_xlabel("Punto (Ubicación)")
ax3.set_ylabel("Cantidad de operaciones")
ax3.set_title(f"Puntos con mayor operaciones en el día {max_day}")
plt.xticks(rotation=45)

# Anotar cada barra con su valor exacto
for bar in bars3:
    height = bar.get_height()
    ax3.annotate(f'{height:.0f}',
                 xy=(bar.get_x() + bar.get_width() / 2, height),
                 xytext=(0, 3), textcoords="offset points",
                 ha='center', va='bottom')

st.pyplot(fig3)
st.write("La tercera gráfica muestra que el dia que hubo mayor cantidad de operaciones fue el 29 de enero de 2022, siendo CC los molinos la sucursal con mas movimiento en dicho dia, con un total de 61 operaciones")

#distribución temporal por hora
# Filtrar datos para incluir solo los top puntos
top_points_names = top_puntos["maplocation_name"].to_list()
datos_top = datos_busiest.filter(pl.col("maplocation_name").is_in(top_points_names))

# Extraer la hora de la operación
datos_top = datos_top.with_columns(
    pl.col("operation_date").dt.hour().alias("hour")
)

fig4, ax4 = plt.subplots(figsize=(10, 6))
ax4.scatter(datos_top["hour"].to_list(), datos_top["maplocation_name"].to_list(), alpha=0.6, color='green')
ax4.set_xlabel("Hora del día")
ax4.set_ylabel("Punto (Ubicación)")
ax4.set_title(f"Distribución temporal de operaciones en los top puntos del día {max_day}")
st.pyplot(fig4)
st.write("La cuarta gráfica ilustra la distribución temporal de las operaciones en los puntos para el día de mayor actividad. Permite observar en qué horas se concentran las transacciones en cada ubicación, ofreciendo una visión detallada de la dinámica horaria.")
