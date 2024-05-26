import streamlit as st
import plotly.express as px
import pandas as pd
import datetime
from PIL import Image
import plotly.graph_objects as go
import os
import warnings
import sys
import platform
import sqlite3
import matplotlib.pyplot as plt
import plotly.figure_factory as ff
warnings.filterwarnings('ignore')

st.set_page_config(page_title="ElectroDunas", page_icon=":bar_chart:",layout="wide")

#st.title(" :bar_chart: ElectroDunas")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)

con = sqlite3.connect('f:/UniAndes/ProyectoAplicado/Proyecto/VSCode_Proyecto/Clientes.db')
df = pd.read_sql_query ("SELECT * FROM ClientesF", con)
#print(df)

## Logo Tittle
image = Image.open('ElectroDunasLogo.jpg')
col1, col2 = st.columns((2))
with col1:
    st.image(image, width=600) 
with col2:
    st.title("")

st.subheader("Fechas de consulta")
## create new column fecha_ymd
df['fecha_ymd'] = df.iloc[:, 1].str[:10]

col1, col2 = st.columns((2))
df["fecha_ymd"] = pd.to_datetime(df["fecha_ymd"])

# Getting the min and max fecha_ymd 
startDate = pd.to_datetime(df["fecha_ymd"]).min()
endDate = pd.to_datetime(df["fecha_ymd"]).max()

with col1:
    date1 = pd.to_datetime(st.date_input("Fecha Inicio", startDate))
with col2:
    date2 = pd.to_datetime(st.date_input("Fecha Fin", endDate))

df = df[(df["fecha_ymd"] >= date1) & (df["fecha_ymd"] <= date2)].copy()

# SideBar Filters
st.sidebar.header("Escoge tu filtro: ")
# Choose Sector
sector = st.sidebar.multiselect("Escoge el Sector", df["SectorD"].unique())
if not sector:
    df2 = df.copy()
else:
    df2 = df[df["SectorD"].isin(sector)]

# Choose Cliente
cliente = st.sidebar.multiselect("Escoge el Cliente", df2["ClientesD"].unique())
if not cliente:
    df3 = df2.copy()
else:
    df3 = df2[df2["ClientesD"].isin(cliente)]

# Filter the data based on sector and cliente
if not sector and not cliente:
    filtered_df0 = df
elif sector and not cliente:
    filtered_df0 = df[df["SectorD"].isin(sector)]
elif not sector and cliente:
    filtered_df0 = df[df["ClientesD"].isin(cliente)]
else:
    filtered_df0 = df3[df["SectorD"].isin(sector) & df3["ClientesD"].isin(cliente)]

filtered_df = filtered_df0.sort_values(by='Fecha', ascending=True)
print(filtered_df.head(50))

cluster_df = filtered_df.groupby(by = ["Cluster"], as_index = False)["Active_energy"].sum()

# ClusterHistogram - SectorDonut -- Graphics
with col1:
    st.subheader("Detalles de Clusters")
    st.caption("Información de consumo de energia por cluster")
    fig = px.bar(cluster_df, x = "Cluster", y = "Active_energy", text = ['${:,.2f}'.format(x) for x in cluster_df["Active_energy"]],
                 template = "seaborn")
    st.plotly_chart(fig,use_container_width=True, height = 200)

with col2:
    st.subheader("Detalles de Sectores")
    st.caption("Porcentaje de consumo de energia por sector")
    fig = px.pie(filtered_df, values = "Active_energy", names = "SectorD", hole = 0.5)
    fig.update_traces(text = filtered_df["SectorD"], textposition = "outside")
    st.plotly_chart(fig,use_container_width=True)

cl1, cl2 = st.columns((2))

# ClusterHistogram - SectorDonut -- DataGrids
cl1, cl2 = st.columns((2))
with cl1:
    with st.expander("Datos de Clusters"):
        st.write(cluster_df.style.background_gradient(cmap="Blues"))
        csv = cluster_df.to_csv(index = False).encode('utf-8')
        st.download_button("Descargar Datos", data = csv, file_name = "Cluster.csv", mime = "text/csv",
                            help = 'Click para descargar datos en formato CSV')

with cl2:
    with st.expander("Datos de Sectores"):
        sector = filtered_df.groupby(by = "SectorD", as_index = False)["Active_energy"].sum()
        st.write(sector.style.background_gradient(cmap="Oranges"))
        csv = sector.to_csv(index = False).encode('utf-8')
        st.download_button("Descargar Datos", data = csv, file_name = "Sector.csv", mime = "text/csv",
                        help = 'Click para descargar datos en formato CSV')

# TimeSeries        
#filtered_df["month_year"] = filtered_df["fecha_ymd"].dt.to_period("M")
filtered_df["month_year"] = filtered_df["fecha_ymd"]
st.subheader('Análisis de Consumos')
st.caption("Información de histórico de consumo de energía por mes")
linechart = pd.DataFrame(filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b"))["Active_energy"].sum()).reset_index()
fig2 = px.line(linechart, x = "month_year", y="Active_energy", labels = {"Active_energy": "kWh"},height=500, width = 1000,template="gridon")
st.plotly_chart(fig2,use_container_width=True)

with st.expander("Datos de Consumos:"):
    st.write(linechart.T.style.background_gradient(cmap="Blues"))
    csv = linechart.to_csv(index=False).encode("utf-8")
    st.download_button('Descargar Datos', data = csv, file_name = "Consumos.csv", mime ='text/csv') 
       
# Treem based on Sector, Cluster, and Cliente
st.subheader("Detalle Sector - Cluster - Cliente")
st.caption("Información de Sectores productivos con los clusters y clientes correspondientes")
fig3 = px.treemap(filtered_df, path = ["SectorD","Cluster","ClientesD"], values = "Active_energy", hover_data = ["Active_energy"], color = "ClientesD")
fig3.update_layout(width = 800, height = 650)
st.plotly_chart(fig3, use_container_width=True)

# HorizontalHistograms for Sector, and Cliente
st.subheader("Detalles de Sectores")
st.caption("Información de consumo de energía por sectores productivos")
fig3 = px.bar(filtered_df, x = "Active_energy", y = "SectorD", orientation='h' )
st.plotly_chart(fig3, use_container_width=True)

st.subheader("Detalles de Clientes")
st.caption("Información de consumo de energía por clientes")
fig4 = px.bar(filtered_df, x = "Active_energy", y = "ClientesD", orientation='h' )
st.plotly_chart(fig4, use_container_width=True)


# Anomalies Graphic
st.subheader('Análisis de Anomalías')
st.caption("Histórico de consumos y anomalías")
anomalia=1

filtered_df = df[df["SectorD"].isin(sector)]

df_anom = filtered_df[filtered_df['Anomalo'].isin(anomalia)]
print(df_anom.head(10))
df_agg_anom = df_anom.groupby('fecha_ymd')['Active_energy'].sum().reset_index()

#df_no_anom = filtered_df[filtered_df['Anomalo'] == 0]
df_no_anom = filtered_df[filtered_df['Anomalo'].isnotin(anomalia)]
print(df_no_anom.head(10))
df_agg_no_anom = df_no_anom.groupby('fecha_ymd')['Active_energy'].sum().reset_index()


