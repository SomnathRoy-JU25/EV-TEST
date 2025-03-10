import streamlit as st
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
from utils.data_processor import load_and_process_data, generate_summary_stats
from utils.visualizations import (
    plot_ev_by_make, 
    plot_ev_by_model_year, 
    plot_ev_by_electric_range, 
    plot_ev_geographical_distribution,
    plot_ev_by_electric_type,
    plot_ev_by_cafv_eligibility,
    plot_interactive_geographic_heatmap
)

# Page configuration
st.set_page_config(
    page_title="EV Population Dashboard",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #4CAF50;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #1E88E5;
        margin-bottom: 1rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        border-radius: 5px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stMetric {
        background-color: white !important;
        border-radius: 5px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stAlert {
        padding: 10px !important;
    }
</style>
""", unsafe_allow_html=True)

# Dashboard header with SVG icon
st.markdown("""
<div style="display: flex; align-items: center; justify-content: center; margin-bottom: 1rem;">
    <svg width="50" height="50" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M19 17H21V19H3V17H5M10 7H14M12 17V5M17 17H7V13H17V17Z" stroke="#4CAF50" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
    <h1 class="main-header">Electric Vehicle Population Dashboard</h1>
</div>
""", unsafe_allow_html=True)

st.markdown("### Analyze and visualize key insights from the Electric Vehicle (EV) population dataset")

# Sidebar for filters and controls
st.sidebar.title("Controls & Filters")

# Load data from assets directory
data_path = "assets/Electric_Vehicle_Population_Data.csv"

# Load and process data
with st.spinner("Processing data..."):
    try:
        # Check if we have the dataset in assets
        if os.path.exists(data_path):
            df = load_and_process_data(data_path)
            st.success(f"Successfully loaded data with {len(df)} records")
        else:
            # Fallback to file upload if dataset doesn't exist in assets
            uploaded_file = st.sidebar.file_uploader("Upload EV Population CSV", type=["csv"])
            if not uploaded_file:
                st.warning("Please upload an Electric Vehicle Population dataset CSV file to begin analysis.")
                st.info("The dashboard expects a CSV file with columns such as Make, Model, Model Year, Electric Range, etc.")
                st.stop()
            df = load_and_process_data(uploaded_file)
            st.success(f"Successfully loaded data from uploaded file with {len(df)} records")
        
        # Save summary stats
        summary_stats = generate_summary_stats(df)
    except Exception as e:
        st.error(f"Error processing data: {str(e)}")
        st.stop()

# Sidebar filters
st.sidebar.subheader("Data Filters")

# Year range filter
min_year = int(df['Model Year'].min())
max_year = int(df['Model Year'].max())
year_range = st.sidebar.slider(
    "Select Model Year Range",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

# Make filter
all_makes = sorted(df['Make'].unique().tolist())
selected_makes = st.sidebar.multiselect(
    "Select Vehicle Makes",
    options=all_makes,
    default=all_makes[:5] if len(all_makes) > 5 else all_makes
)

# Electric Range filter
min_range = int(df['Electric Range'].min())
max_range = int(df['Electric Range'].max())
electric_range = st.sidebar.slider(
    "Select Electric Range (miles)",
    min_value=min_range,
    max_value=max_range,
    value=(min_range, max_range)
)

# Apply filters
filtered_df = df[
    (df['Model Year'] >= year_range[0]) & 
    (df['Model Year'] <= year_range[1]) &
    (df['Make'].isin(selected_makes)) &
    (df['Electric Range'] >= electric_range[0]) &
    (df['Electric Range'] <= electric_range[1])
]

# Display count of filtered data
st.sidebar.info(f"Showing {len(filtered_df)} vehicles out of {len(df)} total")

# Main dashboard content
if not filtered_df.empty:
    # Key metrics row
    st.markdown("<h2 class='sub-header'>Key Metrics</h2>", unsafe_allow_html=True)
    
    metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
    
    with metrics_col1:
        st.metric("Total EVs", f"{len(filtered_df):,}")
    
    with metrics_col2:
        st.metric("Unique Makes", f"{filtered_df['Make'].nunique():,}")
    
    with metrics_col3:
        st.metric("Avg Electric Range", f"{filtered_df['Electric Range'].mean():.1f} miles")
    
    with metrics_col4:
        latest_year = filtered_df['Model Year'].max()
        latest_year_count = len(filtered_df[filtered_df['Model Year'] == latest_year])
        st.metric(f"{latest_year} Models", f"{latest_year_count:,}")
    
    # First row of visualizations
    st.markdown("<h2 class='sub-header'>Distribution Analysis</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
        st.subheader("EVs by Manufacturer")
        fig1 = plot_ev_by_make(filtered_df)
        st.plotly_chart(fig1, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
        st.subheader("EVs by Model Year")
        fig2 = plot_ev_by_model_year(filtered_df)
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Second row of visualizations
    st.markdown("<h2 class='sub-header'>Performance & Technology</h2>", unsafe_allow_html=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
        st.subheader("Electric Range Distribution")
        fig3 = plot_ev_by_electric_range(filtered_df)
        st.plotly_chart(fig3, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col4:
        st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
        st.subheader("EV Type Distribution")
        fig4 = plot_ev_by_electric_type(filtered_df)
        st.plotly_chart(fig4, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Third row of visualizations
    st.markdown("<h2 class='sub-header'>Location & Eligibility</h2>", unsafe_allow_html=True)
    
    col5, col6 = st.columns(2)
    
    with col5:
        st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
        st.subheader("Geographical Distribution")
        fig5 = plot_ev_geographical_distribution(filtered_df)
        st.plotly_chart(fig5, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col6:
        st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
        st.subheader("CAFV Eligibility")
        fig6 = plot_ev_by_cafv_eligibility(filtered_df)
        st.plotly_chart(fig6, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Data exploration section
    st.markdown("<h2 class='sub-header'>Data Explorer</h2>", unsafe_allow_html=True)
    
    st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
    if st.checkbox("Show raw data"):
        st.write(filtered_df)
    
    # Column selector for detailed exploration
    explore_col = st.selectbox(
        "Select column to explore distribution:",
        options=[col for col in filtered_df.columns if col not in ['VIN (1-10)', 'Model']]
    )
    
    if explore_col:
        st.subheader(f"Distribution of {explore_col}")
        
        # Different visualization based on column type
        if filtered_df[explore_col].dtype == 'object':
            # For categorical columns
            value_counts = filtered_df[explore_col].value_counts().reset_index()
            value_counts.columns = [explore_col, 'Count']
            
            # Only show top 20 if there are many unique values
            if len(value_counts) > 20:
                st.info(f"Showing top 20 out of {len(value_counts)} unique values")
                value_counts = value_counts.head(20)
            
            import plotly.express as px
            fig = px.bar(
                value_counts, 
                x=explore_col, 
                y='Count',
                color='Count',
                color_continuous_scale='Viridis'
            )
            fig.update_layout(xaxis_title=explore_col, yaxis_title='Count')
            st.plotly_chart(fig, use_container_width=True)
        else:
            # For numerical columns
            import plotly.figure_factory as ff
            
            fig = ff.create_distplot(
                [filtered_df[explore_col].dropna()], 
                [explore_col],
                bin_size=[max(1, int((filtered_df[explore_col].max() - filtered_df[explore_col].min()) / 50))]
            )
            fig.update_layout(title_text=f'Distribution of {explore_col}')
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Add footer with data information
    st.markdown("---")
    st.markdown(f"**Data Summary:** Dataset contains information on {len(df)} electric vehicles with {df['Make'].nunique()} different manufacturers.")
    
else:
    st.warning("No data available with the current filter settings. Please adjust your filters.")

# Add insights section
st.markdown("<h2 class='sub-header'>Key Insights</h2>", unsafe_allow_html=True)
st.markdown("<div class='metric-container'>", unsafe_allow_html=True)

# Create tabs for different insights
insight_tab1, insight_tab2, insight_tab3 = st.tabs(["EV Adoption Trends", "Regional Analysis", "Technology Progress"])

with insight_tab1:
    st.subheader("EV Adoption Over Time")
    
    # Calculate year-over-year growth
    yearly_counts = df.groupby('Model Year').size().reset_index(name='Count')
    yearly_counts['YoY_Growth'] = yearly_counts['Count'].pct_change() * 100
    
    # Display growth statistics
    year_growth_cols = st.columns(2)
    
    with year_growth_cols[0]:
        # Last complete year data
        max_complete_year = max_year - 1 if max_year == df['Model Year'].max() else max_year
        latest_year_growth = yearly_counts[yearly_counts['Model Year'] == max_complete_year]['YoY_Growth'].values[0] if len(yearly_counts[yearly_counts['Model Year'] == max_complete_year]) > 0 else 0
        
        growth_color = "green" if latest_year_growth >= 0 else "red"
        st.markdown(f"<h3 style='text-align: center; color: {growth_color};'>{latest_year_growth:.1f}%</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center;'>YoY Growth in {max_complete_year}</p>", unsafe_allow_html=True)
    
    with year_growth_cols[1]:
        # Calculate compound annual growth rate over last 5 years
        last_5_years = yearly_counts[yearly_counts['Model Year'] >= max_year - 5]
        if len(last_5_years) >= 2:
            first_year_count = last_5_years.iloc[0]['Count']
            last_year_count = last_5_years.iloc[-1]['Count']
            years_diff = last_5_years.iloc[-1]['Model Year'] - last_5_years.iloc[0]['Model Year']
            if years_diff > 0 and first_year_count > 0:
                cagr = (((last_year_count / first_year_count) ** (1 / years_diff)) - 1) * 100
                st.markdown(f"<h3 style='text-align: center; color: green;'>{cagr:.1f}%</h3>", unsafe_allow_html=True)
                st.markdown(f"<p style='text-align: center;'>5-Year CAGR</p>", unsafe_allow_html=True)
    
    # Display growth chart
    fig_growth = px.bar(
        yearly_counts,
        x='Model Year',
        y='Count',
        title='Yearly EV Registrations'
    )
    # Add growth rate line on secondary y-axis
    fig_growth.add_trace(
        go.Scatter(
            x=yearly_counts['Model Year'],
            y=yearly_counts['YoY_Growth'],
            mode='lines+markers',
            name='YoY Growth %',
            yaxis='y2'
        )
    )
    # Update layout for dual y-axis
    fig_growth.update_layout(
        yaxis=dict(title='Number of Vehicles'),
        yaxis2=dict(
            title='YoY Growth %',
            overlaying='y',
            side='right',
            showgrid=False
        ),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )
    st.plotly_chart(fig_growth, use_container_width=True)

with insight_tab2:
    st.subheader("Regional Adoption Patterns")
    
    # Create columns for regional analysis
    regional_cols = st.columns(2)
    
    with regional_cols[0]:
        # Top 10 counties bar chart
        if 'County' in df.columns:
            county_data = df['County'].value_counts().head(10).reset_index()
            county_data.columns = ['County', 'Count']
            
            fig_counties = px.bar(
                county_data,
                y='County',
                x='Count',
                orientation='h',
                color='Count',
                color_continuous_scale='Viridis',
                title='Top 10 Counties by EV Adoption'
            )
            fig_counties.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_counties, use_container_width=True)
    
    with regional_cols[1]:
        # City vs. County analysis
        if 'City' in df.columns and 'County' in df.columns:
            # Get top 5 counties
            top_counties = df['County'].value_counts().head(5).index.tolist()
            # Filter for those counties
            county_city_data = df[df['County'].isin(top_counties)]
            # Group by county and city
            county_city_counts = county_city_data.groupby(['County', 'City']).size().reset_index(name='Count')
            # Get top 3 cities per county
            top_cities_per_county = county_city_counts.sort_values(['County', 'Count'], ascending=[True, False])
            top_cities_per_county = top_cities_per_county.groupby('County').head(3)
            
            fig_county_city = px.bar(
                top_cities_per_county,
                x='County',
                y='Count',
                color='City',
                title='Top Cities per County',
                barmode='group'
            )
            st.plotly_chart(fig_county_city, use_container_width=True)

with insight_tab3:
    st.subheader("EV Technology Advancement")
    
    # Calculate average electric range by year
    range_by_year = df.groupby('Model Year')['Electric Range'].mean().reset_index()
    range_by_year = range_by_year[range_by_year['Electric Range'] > 0]  # Filter out years with missing data
    
    # Create visualization
    fig_range_trend = px.line(
        range_by_year,
        x='Model Year',
        y='Electric Range',
        markers=True,
        title='Average Electric Range by Model Year'
    )
    fig_range_trend.update_layout(
        xaxis_title="Model Year",
        yaxis_title="Average Range (miles)",
        hovermode="x unified"
    )
    st.plotly_chart(fig_range_trend, use_container_width=True)
    
    # BEV vs PHEV comparison if data is available
    if 'Electric Vehicle Type' in df.columns:
        # Filter for only rows with valid range data
        valid_range_df = df[df['Electric Range'] > 0]
        # Group by type and year
        type_year_range = valid_range_df.groupby(['Electric Vehicle Type', 'Model Year'])['Electric Range'].mean().reset_index()
        # Pivot for better plotting
        ev_type_data = type_year_range.pivot(index='Model Year', columns='Electric Vehicle Type', values='Electric Range').reset_index()
        ev_type_data = ev_type_data.melt(id_vars=['Model Year'], var_name='EV Type', value_name='Avg Range')
        ev_type_data = ev_type_data.dropna()
        
        # Create line chart comparing BEV and PHEV ranges
        fig_type_range = px.line(
            ev_type_data,
            x='Model Year',
            y='Avg Range',
            color='EV Type',
            title='BEV vs PHEV: Average Range Comparison',
            markers=True
        )
        fig_type_range.update_layout(
            xaxis_title="Model Year",
            yaxis_title="Average Range (miles)",
            hovermode="x unified"
        )
        st.plotly_chart(fig_type_range, use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)

# Add an expandable section for data dictionary/explanation
with st.expander("About the Dataset"):
    st.markdown("""
    ### Electric Vehicle Population Data
    
    This dataset provides information about electric vehicles that have been registered with the Department of Licensing.
    
    #### Key Columns:
    - **Make**: The manufacturer of the vehicle
    - **Model**: The model of the vehicle
    - **Model Year**: The model year of the vehicle
    - **Electric Range**: The maximum range of the vehicle in miles on a full charge
    - **Electric Vehicle Type**: Battery Electric Vehicle (BEV) or Plug-in Hybrid Electric Vehicle (PHEV)
    - **CAFV Eligibility**: Clean Alternative Fuel Vehicle (CAFV) eligibility
    - **County**: The county where the vehicle is registered
    - **City**: The city where the vehicle is registered
    - **State**: The state where the vehicle is registered
    - **Postal Code**: The ZIP code where the vehicle is registered
    
    The data provides insights into the adoption of electric vehicles, their geographical distribution, and the progression of EV technology over time.
    """)
