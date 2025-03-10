import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import re

def plot_ev_by_make(df):
    """
    Create a bar chart of EVs by manufacturer.
    
    Args:
        df: Processed pandas DataFrame
        
    Returns:
        Plotly figure object
    """
    # Get top 15 manufacturers by count
    top_makes = df['Make'].value_counts().head(15).reset_index()
    top_makes.columns = ['Make', 'Count']
    
    # Create bar chart
    fig = px.bar(
        top_makes,
        y='Make',
        x='Count',
        orientation='h',
        color='Count',
        color_continuous_scale='Viridis',
        title='Top 15 EV Manufacturers'
    )
    
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        xaxis_title="Number of Vehicles",
        yaxis_title="Manufacturer",
        height=500
    )
    
    return fig

def plot_ev_by_model_year(df):
    """
    Create a line chart of EVs by model year.
    
    Args:
        df: Processed pandas DataFrame
        
    Returns:
        Plotly figure object
    """
    # Group by model year
    year_counts = df.groupby('Model Year').size().reset_index(name='Count')
    
    # Create line chart
    fig = px.line(
        year_counts,
        x='Model Year',
        y='Count',
        markers=True,
        title='EV Adoption by Model Year'
    )
    
    # Add area under the line
    fig.add_trace(
        go.Scatter(
            x=year_counts['Model Year'],
            y=year_counts['Count'],
            fill='tozeroy',
            fillcolor='rgba(0, 176, 246, 0.2)',
            line=dict(color='rgba(0, 176, 246, 0.7)'),
            name='Total EVs'
        )
    )
    
    fig.update_layout(
        xaxis_title="Model Year",
        yaxis_title="Number of Vehicles",
        showlegend=False,
        height=500
    )
    
    # Set x-axis to show every year
    fig.update_xaxes(
        dtick=1,
        tickangle=45
    )
    
    return fig

def plot_ev_by_electric_range(df):
    """
    Create a histogram of electric range distribution.
    
    Args:
        df: Processed pandas DataFrame
        
    Returns:
        Plotly figure object
    """
    # Create histogram
    fig = px.histogram(
        df,
        x='Electric Range',
        nbins=30,
        color_discrete_sequence=['#1E88E5'],
        title='Distribution of Electric Range (miles)'
    )
    
    # Add vertical line for average
    avg_range = df['Electric Range'].mean()
    fig.add_vline(
        x=avg_range,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Avg: {avg_range:.1f} miles",
        annotation_position="top right"
    )
    
    fig.update_layout(
        xaxis_title="Electric Range (miles)",
        yaxis_title="Number of Vehicles",
        height=500
    )
    
    return fig

def plot_ev_geographical_distribution(df):
    """
    Create a choropleth map of geographical distribution.
    
    Args:
        df: Processed pandas DataFrame
        
    Returns:
        Plotly figure object
    """
    # Check if we have good geographical data
    if 'County' in df.columns and df['County'].nunique() > 1:
        geo_level = 'County'
    elif 'City' in df.columns and df['City'].nunique() > 1:
        geo_level = 'City'
    elif 'State' in df.columns and df['State'].nunique() > 1:
        geo_level = 'State'
    elif 'Postal Code' in df.columns and df['Postal Code'].nunique() > 1:
        geo_level = 'Postal Code'
    else:
        # Create a dummy pie chart if no good geo data
        return _create_dummy_geo_chart(df)
    
    # Group by the selected geographical level
    geo_counts = df[geo_level].value_counts().head(15).reset_index()
    geo_counts.columns = [geo_level, 'Count']
    
    # Create bar chart
    fig = px.bar(
        geo_counts,
        y=geo_level,
        x='Count',
        orientation='h',
        color='Count',
        color_continuous_scale='Viridis',
        title=f'Top 15 {geo_level}s with Most EVs'
    )
    
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        xaxis_title="Number of Vehicles",
        yaxis_title=geo_level,
        height=500
    )
    
    return fig

def _create_dummy_geo_chart(df):
    """
    Create a dummy chart when geographical data is not available.
    
    Args:
        df: Processed pandas DataFrame
        
    Returns:
        Plotly figure object
    """
    # Create a simple pie chart of manufacturers
    top_makes = df['Make'].value_counts().head(10).reset_index()
    top_makes.columns = ['Make', 'Count']
    
    fig = px.pie(
        top_makes,
        values='Count',
        names='Make',
        title='Top 10 EV Manufacturers (Geographical data not available)'
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=500)
    
    return fig

def plot_ev_by_electric_type(df):
    """
    Create a pie chart of EV types (BEV vs PHEV).
    
    Args:
        df: Processed pandas DataFrame
        
    Returns:
        Plotly figure object
    """
    # Check if the column exists
    if 'Electric Vehicle Type' not in df.columns:
        # Create a dummy chart
        return _create_dummy_ev_type_chart(df)
    
    # Group by EV type
    type_counts = df['Electric Vehicle Type'].value_counts().reset_index()
    type_counts.columns = ['EV Type', 'Count']
    
    # Create pie chart
    fig = px.pie(
        type_counts,
        values='Count',
        names='EV Type',
        title='Distribution of Electric Vehicle Types',
        color_discrete_sequence=px.colors.sequential.Viridis
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=500)
    
    return fig

def _create_dummy_ev_type_chart(df):
    """
    Create a dummy chart when EV type data is not available.
    
    Args:
        df: Processed pandas DataFrame
        
    Returns:
        Plotly figure object
    """
    # Create a simple bar chart of model years
    year_counts = df.groupby('Model Year').size().reset_index(name='Count')
    
    fig = px.bar(
        year_counts,
        x='Model Year',
        y='Count',
        title='EVs by Model Year (Type data not available)',
        color_discrete_sequence=['#1E88E5']
    )
    
    fig.update_layout(
        xaxis_title="Model Year",
        yaxis_title="Number of Vehicles",
        height=500
    )
    
    return fig

def plot_ev_by_cafv_eligibility(df):
    """
    Create a pie chart of CAFV eligibility.
    
    Args:
        df: Processed pandas DataFrame
        
    Returns:
        Plotly figure object
    """
    # Check if the column exists
    if 'CAFV Eligibility' not in df.columns:
        # Create a dummy chart
        return _create_dummy_cafv_chart(df)
    
    # Group by CAFV eligibility
    cafv_counts = df['CAFV Eligibility'].value_counts().reset_index()
    cafv_counts.columns = ['CAFV Eligibility', 'Count']
    
    # Create pie chart
    fig = px.pie(
        cafv_counts,
        values='Count',
        names='CAFV Eligibility',
        title='Distribution of Clean Alternative Fuel Vehicle Eligibility',
        color_discrete_sequence=px.colors.sequential.Viridis
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=500)
    
    return fig

def _create_dummy_cafv_chart(df):
    """
    Create a dummy chart when CAFV data is not available.
    
    Args:
        df: Processed pandas DataFrame
        
    Returns:
        Plotly figure object
    """
    # Create a simple bar chart of electric range distribution
    fig = px.histogram(
        df,
        x='Electric Range',
        nbins=20,
        title='Electric Range Distribution (CAFV data not available)',
        color_discrete_sequence=['#1E88E5']
    )
    
    fig.update_layout(
        xaxis_title="Electric Range (miles)",
        yaxis_title="Number of Vehicles",
        height=500
    )
    
    return fig

def plot_interactive_geographic_heatmap(df):
    """
    Create an interactive geographic heatmap of EV adoption using lat/long coordinates.
    
    Args:
        df: Processed pandas DataFrame
        
    Returns:
        Plotly figure object
    """
    # Extract coordinates from the Vehicle Location column if it exists
    if 'Vehicle Location' not in df.columns:
        # Fallback to a basic geo chart
        return plot_ev_geographical_distribution(df)
    
    # Extract coordinates using regex pattern
    coordinates_data = []
    
    for loc in df['Vehicle Location']:
        if pd.isna(loc):
            continue
            
        # Extract coordinates using regex
        match = re.search(r'POINT \((-?\d+\.?\d*) (-?\d+\.?\d*)', str(loc))
        if match:
            lon, lat = float(match.group(1)), float(match.group(2))
            coordinates_data.append({'lon': lon, 'lat': lat})
    
    # Create DataFrame from extracted coordinates
    if not coordinates_data:
        # No valid coordinates found, return fallback
        return plot_ev_geographical_distribution(df)
        
    coords_df = pd.DataFrame(coordinates_data)
    
    # Create density heatmap
    fig = px.density_mapbox(
        coords_df, 
        lat='lat', 
        lon='lon', 
        radius=10,
        zoom=7,
        mapbox_style="carto-positron",
        title="EV Geographic Distribution Heatmap",
        height=700
    )
    
    # Improve layout
    fig.update_layout(
        mapbox=dict(
            center=dict(lat=coords_df['lat'].mean(), lon=coords_df['lon'].mean()),
        ),
        margin=dict(l=0, r=0, t=50, b=0)
    )
    
    return fig
