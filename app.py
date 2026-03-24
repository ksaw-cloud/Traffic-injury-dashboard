import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(layout='wide')
st.title('Traffic Injury Dashboard')
st.markdown(
    'Explore traffic injuries by transportation mode and time. '
    'Use filters to update all charts.'
    )

#load and clean data
@st.cache_data
def load_data():
    df = pd.read_csv('road_traffic_small.csv', low_memory=False)
    
    #convert to correct type
    df_clean = df[['reportyear', 'mode', 'severity', 'injuries', 'county_name', 'region_name', 'poprate', 'avmtrate']].copy()
    
    df_clean['reportyear'] = pd.to_numeric(df_clean['reportyear'], errors = 'coerce')
    df_clean['injuries'] = pd.to_numeric(df_clean['injuries'], errors = 'coerce')
    df_clean['poprate'] = pd.to_numeric(df_clean['poprate'], errors = 'coerce')

    #drop missing values
    df_clean = df_clean.dropna(subset=['reportyear', 'injuries'])
    df_clean['reportyear'] = df_clean['reportyear'].astype(int)
    
    return df_clean

df_clean = load_data()

#filters(key)
modes = sorted(df_clean['mode'].dropna().unique())
mode = st.selectbox('Transport Mode', modes, index= 0)

severity = st.selectbox('Severity', sorted(df_clean['severity'].dropna().unique()))

year_min = int(df_clean['reportyear'].min())
year_max = int(df_clean['reportyear'].max())

year_range = st.slider(
    'Year Range',
    min_value = year_min,
    max_value = year_max,
    value=(year_min, year_max))

#Apply filters
filtered = df_clean[
    (df_clean['mode'] == mode) &
    (df_clean['severity'] == severity) &
    (df_clean['reportyear'] >= year_range[0]) &
    (df_clean['reportyear'] <= year_range[1])].copy()

if filtered.empty:
    st.warning('No data available')
    st.stop()

#metrics
colA, colB = st.columns(2)

with colA:
    st.metric('Total Injuries', int(filtered['injuries'].sum()))
with colB:
    st.metric('Average Injuries', round(filtered['injuries'].mean(), 2))

#charts
st.subheader('Trend Analysis')
st.caption('Shows how total injuries change over time based on filters. ')

col1, col2 = st.columns(2)

#line: trend over time
with col1:
    df_line = filtered.groupby('reportyear')['injuries'].sum().reset_index()
    df_line = df_line.sort_values('reportyear')
    fig_line = px.line(df_line, x = 'reportyear', y='injuries', title= f'Injuries Over Time ({mode}, {severity})')
    fig_line.update_layout(xaxis_title ='Year', yaxis_title='Number of Injuries')
    st.plotly_chart(fig_line, width= 'stretch')

#Bar: yearly totals
with col2:
    fig_bar = px.bar(df_line, x='reportyear', y='injuries', title = f'Yearly Injuries ({mode}, {severity})')
    fig_bar.update_layout(xaxis_title='Year', yaxis_title='Number of Injuries')
    st.plotly_chart(fig_bar, width= 'stretch')

st.subheader('Distribution & Relationships')
st.caption('Shows how injuries are distributed and how they relate to population rates across regions. ')

col3, col4 = st.columns(2)

#histogram(log transform)
with col3: 
    hist_df = filtered[filtered['injuries'] > 0].copy()
    hist_df['log_injuries'] = np.log10(hist_df['injuries'])
    fig_hist = px.histogram(
        hist_df, x='log_injuries', nbins = 30, title = 'Distribution of Injuries (Log Transformed)')
    fig_hist.update_layout(xaxis_title='Log10(Injuries)', yaxis_title='Count')
    st.plotly_chart(fig_hist, width= 'stretch')

#scatter: relationship
with col4:
    fig_scatter = px.scatter(
        filtered,
        x='poprate',
        y='injuries',
        color = 'region_name',
        hover_data = ['county_name'],
        title =f'Injuries vs Population Rate ({mode}, {severity})')
    fig_scatter.update_layout(xaxis_title ='Population Rate', yaxis_title='Number of Injuries')
    st.plotly_chart(fig_scatter, width= 'stretch')

