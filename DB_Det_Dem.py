
import glob
import datetime 
import pandas as pd
import datetime as dt 
import numpy as np 
import warnings
import streamlit as st
import plotly.express as px
from io import BytesIO
from pyxlsb import open_workbook as open_xlsb


warnings.filterwarnings('ignore')

DATA_URL = r"\\WNSAN01\Server\Container Planning\output\old_outputs\web\DET.txt"
DATA_URL2 = r"\\WNSAN01\Server\Container Planning\output\old_outputs\web\DEM.txt"
det = pd.read_csv(DATA_URL, sep=",", header=None, index_col=False)
dem = pd.read_csv(DATA_URL2, sep=",", header=None, index_col=False)

Detention = det.rename(columns={1:'Date',2:'Ctr',3:'Type',4:'Size',5:'TEU',6:'Auftragsnummer',
             7:'Forwarder',8:'Main voyage load date',9:'Remarks2_Archiv', 10:'Days in Detention', 11:'Last Day',12:'Cost', 13:'DetentionCost'})


Detention['Date'] ='1800-01-01 00:00:00'

for row in range(len(Detention)):
    if Detention.loc[row, "Date"] ==  '1800-01-01 00:00:00':
        Detention.loc[row, "Date"] = pd.to_datetime(Detention.loc[row,"Main voyage load date"], format="%d.%m.%y") + pd.Timedelta(days=20)

Detention['Date'] =  pd.to_datetime(Detention['Date'], format="%Y-%m-%d %H:%M:%S", errors = 'coerce')
Detention['Week'] = Detention['Date'].dt.isocalendar().week
Detention['Day'] = Detention['Date'].dt.day
Detention['Month'] = Detention['Date'].dt.month
Detention['Year'] = Detention['Date'].dt.year

Detention['Week'] = Detention['Week'].fillna(0)
Detention['Day'] = Detention['Day'].fillna(0)
Detention['Month'] = Detention['Month'].fillna(0)
Detention['Year'] = Detention['Year'].fillna(0)

Detention['Week'] = Detention['Week'].astype(int)
Detention['Day'] = Detention['Day'].astype(int)
Detention['Month'] = Detention['Month'].astype(int)
Detention['Year'] = Detention['Year'].astype(int)

Detention['Auftragsnummer'] = Detention['Auftragsnummer'].astype(str)

Detention = Detention[['Date', 'Week', 'Day', 'Month', 'Year','Ctr', 'Type', 'Size', 
                       'TEU', 'Auftragsnummer', 'Forwarder', 'Main voyage load date',
                       'Remarks2_Archiv', 'Days in Detention', 'Last Day', 'Cost',
                       'DetentionCost']]
					   
					   
					   
Demurrage = dem.rename(columns={1:'Date',2:'Ctr',3:'Type',4:'Size',5:'TEU',6:'Auftragsnummer',
                          7:'Forwarder',8:'Eta Port',9:'Abnahme Seehafen',
                          10:'Allowance', 11:'DemDays',12:'Cost', 13:'DemurrageCost'})

Demurrage["Date"]= pd.to_datetime(Demurrage["Abnahme Seehafen"],
                                  format="%d.%m.%y", errors='coerce')

Demurrage['Week'] = Demurrage['Date'].dt.isocalendar().week
Demurrage['Day'] = Demurrage['Date'].dt.day
Demurrage['Month'] = Demurrage['Date'].dt.month
Demurrage['Year'] = Demurrage['Date'].dt.year

Demurrage['Week'] = Demurrage['Week'].fillna(0)
Demurrage['Day'] = Demurrage['Day'].fillna(0)
Demurrage['Month'] = Demurrage['Month'].fillna(0)
Demurrage['Year'] = Demurrage['Year'].fillna(0)

Demurrage['Week'] = Demurrage['Week'].astype(int)
Demurrage['Day'] = Demurrage['Day'].astype(int)
Demurrage['Month'] = Demurrage['Month'].astype(int)
Demurrage['Year'] = Demurrage['Year'].astype(int)

Demurrage['Auftragsnummer'] = Demurrage['Auftragsnummer'].astype(str)

Demurrage = Demurrage[['Date', 'Ctr', 'Type', 'Size', 'TEU', 'Auftragsnummer',
                       'Forwarder','Eta Port', 'Abnahme Seehafen', 'Allowance',
                       'DemDays', 'Cost', 'DemurrageCost','Week','Day','Month',
                       'Year']]

##############################################################################################################################

st.set_page_config(page_title= "Dem/Det", 
                  page_icon = ":anchor:",
                  layout="wide")

st.sidebar.header("Filter Data Here:")

Yr = Detention["Year"].astype(str).unique()
Yr_chk_list = Yr.tolist()
Yr_chk_list = sorted(Yr_chk_list, reverse=True)

Year = st.sidebar.selectbox("Select Year:", 
                            Yr_chk_list)


source = Detention.copy()
source["Year"] = source["Year"].astype(str)
Year_chk = source[source["Year"] == Year]

#--- Main Page ---
df_selection = source.query("Year==@Year")
df_selection.reset_index(drop=True,inplace=True)
df_selection = df_selection[["Month", "DetentionCost"]]


df_selection = df_selection.groupby(['Month'])['DetentionCost'].sum().reset_index()

fig = px.bar(df_selection, x="Month", y="DetentionCost",title="Detention Costs:"+" "+Year, text_auto= True)
fig.update_layout(yaxis_tickprefix = '€', yaxis_tickformat = ',.0f')
fig.update_yaxes(tickfont=dict(size=20))
fig.update_xaxes(tickfont=dict(size=28), tickvals=['Month'])
fig.update_layout(
	xaxis = dict(
		tickmode = 'array',
		tickvals = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
		ticktext = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
	)
)
fig.update_layout(height=600, width= 1600)

st.write(fig)	

@st.cache
def to_excel(Detention):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    Detention.to_excel(writer, index=False, sheet_name='Sheet1')
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    format1 = workbook.add_format({'num_format': '0.00'}) 
    worksheet.set_column('A:A', None, format1)  
    writer.save()
    processed_data = output.getvalue()
    return processed_data
df_xlsx = to_excel(Detention)
st.download_button(label='📥 Download Current Detention Data',
                                data=df_xlsx ,
                                file_name= 'Detention.xlsx')		
			
			
###################################################################################################################################			
			
			
source2 = Demurrage.copy()
source2["Year"] = source2["Year"].astype(str)
Year_chk = source2[source2["Year"] == Year]

#--- Main Page ---
df_selection = source2.query("Year==@Year")
df_selection.reset_index(drop=True,inplace=True)
df_selection = df_selection[["Month", "DemurrageCost"]]


df_selection = df_selection.groupby(['Month'])['DemurrageCost'].sum().reset_index()

fig2 = px.bar(df_selection, x="Month", y="DemurrageCost", color_discrete_sequence=["crimson"], barmode="relative",
			 title="Demurrage Costs:"+" "+Year, text_auto= True)
fig2.update_layout(yaxis_tickprefix = '€', yaxis_tickformat = ',.0f')
fig2.update_yaxes(tickfont=dict(size=20))
fig2.update_xaxes(tickfont=dict(size=28), tickvals=['Month'])
fig2.update_layout(
	 xaxis = dict(
		 tickmode = 'array',
		 tickvals = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
		 ticktext = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
	)
)
fig2.update_layout(height=600, width= 1600)

st.write(fig2)	

@st.cache
def to_excel(Demurrage):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    Demurrage.to_excel(writer, index=False, sheet_name='Sheet1')
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    format1 = workbook.add_format({'num_format': '0.00'}) 
    worksheet.set_column('A:A', None, format1)  
    writer.save()
    processed_data = output.getvalue()
    return processed_data
df_xlsx = to_excel(Demurrage)
st.download_button(label='📥 Download Current Demurrage Data',
                                data=df_xlsx ,
                                file_name= 'Demurrage.xlsx')			