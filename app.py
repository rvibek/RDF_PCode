import streamlit as st
import pandas as pd
import base64
import plotly.express as px


st.title('RDF PCode Explorer')
st.markdown('This app shows a potential PCODE mismatches in RDF data. For example, a PCODE that is intended to identify a location in one country may be mistakenly assigned to a location in a different country or it may be using HCR3 code for the same country.\n\n The app also highlights empty PCODE instances.')

st.sidebar.title('Apply Filter')
selyear = st.sidebar.selectbox('Select RDF Year',
                    ("2021", "2020", "2019", "2018", "2017", "2016"), index=0)

#read db
@st.cache
def read_data():
    df = df = pd.read_csv('Demographics_merged.csv')
    # df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
    df = df[['Year', 'asylum', 'origin', 'locationClean', 'Total', 'location_pcode', 'iso3_asylum']]

    # replace NaN values with empty string
    df = df.fillna('')
    df['status'] = df.apply(lambda row: row['location_pcode'] in row['iso3_asylum'] or any(x in row['location_pcode'] for x in row['iso3_asylum'].split(', ')), axis=1)
    return df


data = read_data()
# st.write(data.dtypes)

seldata = data[data.Year == selyear]
seldata['Total'] = pd.to_numeric(seldata['Total'])



st.markdown('---')

col1, col2, col3 = st.columns(3)
totalrecord = len(seldata)
emptyrecord = len(seldata[seldata.location_pcode == ''])
mismatchrecord = len(seldata[(seldata.status == False)])


col1.metric("Total records",totalrecord,'', delta_color="off")
col2.metric("Empty PCode", emptyrecord, '', delta_color="off")
col3.metric("Mismatch Pcode", mismatchrecord, '', delta_color="off")

st.markdown('---')


exportdata = seldata[(seldata.status == False) | (seldata.location_pcode == '')]

x=exportdata.iso3_asylum.value_counts().index
y=exportdata.iso3_asylum.value_counts().values

fig = px.bar(x=x, y=y, template='streamlit', hover_name=x, height=300, title="ISO3 with Empty Pcode or PCode mismatch")
st.plotly_chart(fig)


st.markdown('Excerpt of records with PCode mismatches and empty values for the selected year can be downloaded from the link below')
csv = exportdata.to_csv().encode()
b64 = base64.b64encode(csv).decode()
filename = "summary_RDF_"+str(selyear)+".csv"
href = f'<a href="data:file/csv;base64,{b64}" download={filename} target="_blank">Download CSV Excerpt</a>'
st.markdown(href, unsafe_allow_html=True)

st.markdown('---')
st.markdown('Navigate to respective TAB to explore the records in detail')

tab1, tab2 = st.tabs(["Empty PCode", "PCode Mismatch"])
tab1.dataframe(seldata[seldata.location_pcode == ''])

mismatchdf = seldata[(seldata.status == False)]
tab2.dataframe(mismatchdf)