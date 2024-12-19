import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.seasonal import seasonal_decompose

# Data Load
df = pd.read_csv('bls_cleaned_data.csv')

# Map series descriptions to the data
series_descriptions = {
    "CES0000000001": "Total Non-Farm Workers",
    "LNS14000000": "Unemployment Rate",
    "LNS13000000": "Unemployment Level",
    "CES0500000002": "Average weekly hours",}
df['seriesName'] = df['seriesID'].map(series_descriptions)

# Convert date column to datetime format
df['date'] = pd.to_datetime(df['date'])

# Sidebar Filters
st.sidebar.header('Data Filter')
st.sidebar.header("Filters")

# 1. Select Series (Multi-Select Dropdown)
available_series = df['seriesName'].unique()
selected_series = st.sidebar.multiselect("Select Series", available_series, default=available_series)

# 2. Select Date Range (Calendar)
min_date = df['date'].min()
max_date = df['date'].max()
selected_date_range = st.sidebar.date_input("Select Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)

# Filter the data based on selected series and date range
df_filtered = df[df['seriesName'].isin(selected_series)]
df_filtered = df_filtered[(df_filtered['date'] >= pd.to_datetime(selected_date_range[0])) &
                          (df_filtered['date'] <= pd.to_datetime(selected_date_range[1]))]

# Title
st.title("US Labor Statistics Dashboard")
st.write("Interactive visualization of labor statistics data.")

#Tabs

tabs = ['Data Table', 'Charts', 'Relationship Analysis', 'Trend Analysis']
selected_tab = st.radio("Explore the dashboard by selecting a tab", tabs, index=0)

# Chart Tab
if selected_tab == 'Charts':
    st.header("Charts")

    # Filtered data for "Total Non-Farm Workers" and "Unemployment Rate"
    workers_data = df_filtered[df_filtered['seriesName'] == "Total Non-Farm Workers"]
    unemployment_data = df_filtered[df_filtered['seriesName'] == "Unemployment Rate"]

    # Merge the two datasets on the 'date' column to align the data
    merged_data = pd.merge(workers_data[['date', 'value']], unemployment_data[['date', 'value']], on='date',
                           suffixes=('_workers', '_unemployment'))

    # Bar Chart: Filter data for 'Total Non-Farm Workers'
    st.subheader("Bar Chart: Total Non-Farm Workers Over Time")
    st.write("The bar chart to visualize unemployment rate over the last 12 months")

    def plot_bar_chart(data):
        fig_bar = px.bar(
            data, x="date", y="value", color="seriesName",
            title="Trends in Unemployment Rate Over Time (Bar Chart)",
            labels={"value": "Unemployment Rate (%)", "date": "Month", "seriesName": "Series"}
        )
        fig_bar.update_layout(
            xaxis_title="Month",
            yaxis_title="Unemployment Rate (%)",
            xaxis_tickangle=45,
            showlegend=False
        )
        fig_bar.update_yaxes(range=[0, max(data['value']) * 1.1])
        return fig_bar

    bar_chart = plot_bar_chart(df)
    st.plotly_chart(bar_chart)

    # Pie chart
    def plot_pie_chart(data):
        fig_pie = px.pie(
            data,
            names='seriesName',
            values='value',
            title="<b>Labor Force Statistics Distribution</b>",
            color='seriesName',
            color_discrete_sequence=px.colors.qualitative.Set3,  # A more vibrant color palette
            hole=0.1,  # Converts the pie chart into a donut chart for a modern look
        )
        fig_pie.update_traces(
            textinfo='percent+label',  # Display percentage and label on each slice
            hoverinfo='label+value+percent',  # Detailed hover information
            pull=[0.1 if i == 0 else 0 for i in range(len(data))]  # Emphasize the first slice
        )
        fig_pie.update_layout(
            title_font_size=20,
            title_x=0.5,  # Center-align the title
            legend_title="<b>Statistics</b>",
            legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center")  # Horizontal legend below chart
        )
        return fig_pie


    # Streamlit Section
    st.subheader("Labor Force Statistics Distribution (Enhanced Pie Chart)")
    st.write(
        "This donut chart visualizes the proportion of various labor force statistics, providing a clearer overview.")

    # Display the enhanced pie chart
    pie_chart = plot_pie_chart(df)
    st.plotly_chart(pie_chart, use_container_width=True)  # Adjust to fit the container width

    # Histogram
    st.subheader("Histogram with Trend of Total Non-Farm Workers")
    st.write("Distribution of Total Non-Farm Workers")
    fig_hist, ax_hist = plt.subplots(figsize=(10, 6))
    ax_hist.hist(df_filtered['value'], bins=30, color='skyblue', alpha=0.7)
    ax_hist.set_title('Distribution of Total Non-Farm Workers')
    ax_hist.set_xlabel('Value')
    ax_hist.set_ylabel('Frequency')
    st.pyplot(fig_hist)

    # The scatter plot using Seaborn
    st.subheader("Scatter Plot: Relationship Between Total Non-Farm Workers and Unemployment Rate")
    st.write(
        "This scatter plot visualizes the relationship between the total number of non-farm workers "
        "and the unemployment rate over time. Each point represents data for a specific date, where "
        "the x-axis shows the number of non-farm workers, and the y-axis shows the unemployment rate. "
        "A higher concentration of points in a particular area may indicate a stronger correlation between these two variables."
    )
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=merged_data, x='value_workers', y='value_unemployment', color='skyblue')

    #  the title and labels
    plt.title("Scatter Plot: Total Non-Farm Workers vs. Unemployment Rate")
    plt.xlabel("Total Non-Farm Workers")
    plt.ylabel("Unemployment Rate")
    st.pyplot(plt)

# Raw Data Tab
elif selected_tab == 'Data Table':
    st.header("Data Table")
    st.dataframe(df_filtered)

# Relationship Analysis Tab
elif selected_tab == 'Relationship Analysis':
    st.header("💡 Relationship Analysis")
    df_pivot = df_filtered.pivot_table(index='date', columns='seriesID', values='value')
    corr_matrix = df_pivot.corr()
    st.write("Correlation Matrix:")
    st.write(corr_matrix)

    # Visualize the correlation matrix as a heatmap
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', vmin=-1, vmax=1, linewidths=0.5)
    st.pyplot(plt)

    #Trend Analysis Tab
elif selected_tab == 'Trend Analysis':
    st.header("📊 🔍 Trend Analysis")
    st.write("This tab shows the trend analysis of labor statistics over time.")
    selected_series = st.sidebar.multiselect("Select Series to Analyze", options=df['seriesName'].unique(),
                                             default=df['seriesName'].unique())
    filtered_data = df[df['seriesName'].isin(selected_series)]
    # Line Chart for Trend Analysis
    st.header("📈 Labor Force Trends Over Time")
    fig_line = px.line(
        filtered_data, x="date", y="value", color="seriesName",
        title="Labor Force Trends Over Time",
        labels={"value": "Value", "date": "Date", "seriesName": "Series"},
    )
    fig_line.update_yaxes(title="Value", showgrid=True)
    st.plotly_chart(fig_line)

    # Seasonal Decomposition
    st.header("📉 Seasonal Decomposition (Holt-Winters Exponential Smoothing)")
    # Filter data for a specific series (e.g., Total Non-Farm Workers)
    df_filtered = filtered_data[filtered_data['seriesName'] == "Total Non-Farm Workers"]
    df_filtered = df_filtered[['date', 'value']].set_index('date')
    df_filtered = df_filtered.resample('M').mean()  # Resample by month
    df_filtered['value'] = df_filtered['value'].interpolate(method='linear')

    # Apply Holt-Winters Exponential Smoothing for forecasting
    if not df_filtered.empty:
        model = ExponentialSmoothing(df_filtered['value'], trend='add', seasonal='add', seasonal_periods=12)
        model_fit = model.fit()

        # Forecast for the next 12 months
        forecast = model_fit.forecast(12)
        fig_forecast, ax_forecast = plt.subplots(figsize=(10, 6))
        ax_forecast.plot(df_filtered.index, df_filtered['value'], label='Historical Data', color='blue')
        ax_forecast.plot(forecast.index, forecast, label='Forecast', linestyle='--', color='red')
        ax_forecast.set_title('Holt-Winters Exponential Smoothing Forecast for Total Non-Farm Workers')
        ax_forecast.set_xlabel('Date')
        ax_forecast.set_ylabel('Total Non-Farm Workers')
        ax_forecast.legend(loc='upper left')
        st.pyplot(fig_forecast)

        # Visualizing Seasonal Trends
        st.header("🔄 Seasonal Trends Analysis")
        df_filtered['seasonal'] = model_fit.fittedvalues - model_fit.trend
        fig_seasonal, ax_seasonal = plt.subplots(figsize=(10, 6))
        ax_seasonal.plot(df_filtered.index, df_filtered['seasonal'], label='Seasonal Component', color='green')
        ax_seasonal.set_title('Seasonal Component of Total Non-Farm Workers')
        ax_seasonal.set_xlabel('Date')
        ax_seasonal.set_ylabel('Seasonality')
        ax_seasonal.legend(loc='upper left')
        st.pyplot(fig_seasonal)

        # Visualizing the Trend Component
        st.header("📊 Trend Component")
        df_filtered['trend'] = model_fit.trend
        fig_trend, ax_trend = plt.subplots(figsize=(10, 6))
        ax_trend.plot(df_filtered.index, df_filtered['trend'], label='Trend Component', color='orange')
        ax_trend.set_title('Trend Component of Total Non-Farm Workers')
        ax_trend.set_xlabel('Date')
        ax_trend.set_ylabel('Trend')
        ax_trend.legend(loc='upper left')
        st.pyplot(fig_trend)

        # Summary or Insights
        st.header("📃 Insights and Summary")

        # Additional insights, such as seasonal patterns or trends in the data
        seasonal_pattern = df_filtered['seasonal'].mean()
        trend_value = df_filtered['trend'].iloc[-1]
        st.write(f"The average seasonal component over the period is {seasonal_pattern:.2f}.")
        st.write(f"The latest trend value for 'Total Non-Farm Workers' is {trend_value:.2f}.")
    else:
        st.write("No Data available for selected series.")

st.sidebar.markdown('''
   ---
   Created By Reshmi Deb
   ''')



# ---------------- Footer ----------------
st.divider()
st.markdown("**Labor Statistics Dashboard** | Built with 💻 Streamlit")
