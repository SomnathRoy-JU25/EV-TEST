import pandas as pd
import numpy as np
import streamlit as st

def load_and_process_data(file):
    """
    Load and process the EV population data.
    
    Args:
        file: Uploaded file object
        
    Returns:
        Processed pandas DataFrame
    """
    # Load the CSV file
    df = pd.read_csv(file)
    
    # Rename columns if they have different names than expected
    # This is to handle potential variations in column naming
    column_mapping = {
        'Vehicle Make': 'Make',
        'Vehicle Model': 'Model',
        'Vehicle Year': 'Model Year',
        'Electric Vehicle Range': 'Electric Range',
        'Electric Vehicle Type': 'Electric Vehicle Type',
        'Clean Alternative Fuel Vehicle Eligibility': 'CAFV Eligibility',
        'Vehicle Location': 'Location',
        'Vehicle VIN': 'VIN (1-10)',
        'DOL Vehicle ID': 'DOL Vehicle ID',
        'Legislative District': 'Legislative District'
    }
    
    # Apply column mapping for columns that exist
    for old_col, new_col in column_mapping.items():
        if old_col in df.columns and new_col not in df.columns:
            df.rename(columns={old_col: new_col}, inplace=True)
    
    # Check for required columns
    required_columns = ['Make', 'Model', 'Model Year']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
    
    # Ensure electric range column exists, create if it doesn't
    if 'Electric Range' not in df.columns:
        # Try to find a column that might contain range information
        range_columns = [col for col in df.columns if 'range' in col.lower()]
        if range_columns:
            df.rename(columns={range_columns[0]: 'Electric Range'}, inplace=True)
        else:
            # Create a dummy Electric Range column if it doesn't exist
            st.warning("Electric Range column not found. Creating a placeholder column.")
            df['Electric Range'] = np.nan
    
    # Clean and convert data types
    
    # Convert Model Year to numeric, handling errors
    df['Model Year'] = pd.to_numeric(df['Model Year'], errors='coerce')
    
    # Convert Electric Range to numeric, handling errors
    df['Electric Range'] = pd.to_numeric(df['Electric Range'], errors='coerce')
    
    # Fill missing numeric values with appropriate defaults
    # Using the recommended approach to avoid pandas FutureWarning
    df = df.copy()  # Create a copy to avoid chained assignment warnings
    model_year_median = df['Model Year'].median()
    electric_range_median = df['Electric Range'].median()
    
    df['Model Year'] = df['Model Year'].fillna(model_year_median)
    df['Electric Range'] = df['Electric Range'].fillna(electric_range_median)
    
    # Ensure Make and Model are strings
    df['Make'] = df['Make'].astype(str)
    df['Model'] = df['Model'].astype(str)
    
    # Ensure EV type column exists
    if 'Electric Vehicle Type' not in df.columns:
        # Try to find a column that might contain type information
        type_columns = [col for col in df.columns if 'type' in col.lower() or 'category' in col.lower()]
        if type_columns:
            df.rename(columns={type_columns[0]: 'Electric Vehicle Type'}, inplace=True)
        else:
            # Create a dummy EV Type column if it doesn't exist
            st.warning("Electric Vehicle Type column not found. Creating a placeholder column.")
            df['Electric Vehicle Type'] = 'Unknown'
    
    # Ensure CAFV eligibility column exists
    if 'CAFV Eligibility' not in df.columns:
        # Create a dummy CAFV eligibility column if it doesn't exist
        st.warning("CAFV Eligibility column not found. Creating a placeholder column.")
        df['CAFV Eligibility'] = 'Unknown'
    
    # Handle geographical data
    geo_columns = ['County', 'City', 'State', 'Postal Code']
    for col in geo_columns:
        if col not in df.columns:
            df[col] = 'Unknown'
    
    return df

def generate_summary_stats(df):
    """
    Generate summary statistics for the EV population data.
    
    Args:
        df: Processed pandas DataFrame
        
    Returns:
        Dictionary of summary statistics
    """
    summary = {}
    
    # Total number of EVs
    summary['total_evs'] = len(df)
    
    # Unique makes and models
    summary['unique_makes'] = df['Make'].nunique()
    summary['unique_models'] = df['Model'].nunique()
    
    # Average electric range
    summary['avg_electric_range'] = df['Electric Range'].mean()
    
    # Most common make
    most_common_make = df['Make'].value_counts().index[0]
    summary['most_common_make'] = most_common_make
    summary['most_common_make_count'] = df[df['Make'] == most_common_make].shape[0]
    
    # Year statistics
    summary['min_year'] = df['Model Year'].min()
    summary['max_year'] = df['Model Year'].max()
    summary['median_year'] = df['Model Year'].median()
    
    # Electric Vehicle Type distribution
    if 'Electric Vehicle Type' in df.columns:
        ev_types = df['Electric Vehicle Type'].value_counts().to_dict()
        summary['ev_type_distribution'] = ev_types
    
    # CAFV Eligibility distribution
    if 'CAFV Eligibility' in df.columns:
        cafv_eligibility = df['CAFV Eligibility'].value_counts().to_dict()
        summary['cafv_eligibility_distribution'] = cafv_eligibility
    
    # Geographical statistics
    if 'County' in df.columns:
        top_counties = df['County'].value_counts().head(5).to_dict()
        summary['top_counties'] = top_counties
    
    if 'City' in df.columns:
        top_cities = df['City'].value_counts().head(5).to_dict()
        summary['top_cities'] = top_cities
    
    if 'State' in df.columns and df['State'].nunique() > 1:
        top_states = df['State'].value_counts().head(5).to_dict()
        summary['top_states'] = top_states
    
    return summary
