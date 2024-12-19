import streamlit as st
import pandas as pd
import plotly.express as px

try:
    df = pd.read_csv("data/bls_cleaned_data.csv")
    df['date'] = pd.to_datetime(df['date'], errors='coerce')  # Ensure date is in datetime format
    if df['date'].isnull().any():
        raise ValueError("The 'date' column contains invalid or missing values.")
except FileNotFoundError:
    st.error("The file 'bls_cleaned_data.csv' was not found. Please ensure you have processed the data.")
    st.stop()
except ValueError as e:
    st.error(str(e))
    st.stop()

    st.title("US Labor Statistics")
    st.write("Interactive visualization of labor statistics data.")
    st.sidebar.header('Dashboard')
    st.sidebar.subheader('Heat map parameter')
    time_hist_color = st.sidebar.selectbox('color by', ("Unemployment Rate", "Non-Farm Workers"), index=0)
    st.sidebar.subheader('Donut chart parameter')
    donut_thete = st.sidebar.selectbox('Select data for distribution:', ("Unemployment Rate", "Non-Farm Workers"))
    st.sidebar.subheader('Line chart parameter')
    plot_data = st.sidebar.multiselect('Select Series', ('Total Non-Farm Workers', 'Unemployment Rates'))
    plot_height = st.sidebar.slider('Specify plot height', 200, 500, 250)

    st.sidebar.markdown('''
    ---
    Created By Reshmi Deb
    ''')

    # Row A
    st.markdown('### Metrics')
    col1, col2, col3 = st.columns(3)
    col1.metric("Unemployment Rate", "")