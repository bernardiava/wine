"""
Global Wine Markets Database Analysis Dashboard
===============================================
A comprehensive Streamlit application for analyzing global wine market data from 1835-2024.

This dashboard provides:
- Interactive visualizations of wine production, consumption, trade, and vineyard areas
- Regional and country-level analysis
- Economic indicators and comparative advantage metrics
- 5-level expert analysis framework for agricultural and regional economics

Data Source: Annual Database of Global Wine Markets, 1835 to 2024
Authors: Kym Anderson and Vicente Pinilla (with assistance from Alexander Holmes)
Institution: Wine Economics Research Centre, University of Adelaide
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Global Wine Markets Analysis Dashboard",
    page_icon="🍷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #722F37;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #8B4513;
        margin-top: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .analysis-box {
        background-color: #fff5f5;
        border-left: 4px solid #722F37;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Cache data loading functions
@st.cache_data
def load_sheet(sheet_name):
    """Load a specific sheet from the Excel file."""
    df = pd.read_excel(
        'megafile_of_global_wine_data_1835_to_2024-0425.xlsx',
        sheet_name=sheet_name,
        header=None
    )
    return df

@st.cache_data
def process_table(table_code, table_name):
    """Process a table into a clean DataFrame with years as index and countries as columns."""
    df = load_sheet(table_name)
    
    # Extract headers (row 1 contains country names, row 2+ contains data)
    countries = df.iloc[1].tolist()
    
    # Create DataFrame starting from row 2
    data_df = df.iloc[2:].copy()
    data_df.columns = countries
    
    # First column is year
    year_col = data_df.iloc[:, 0]
    data_df['Year'] = pd.to_numeric(year_col, errors='coerce')
    
    # Set Year as index
    data_df = data_df.set_index('Year')
    
    # Convert all columns to numeric, handling potential issues
    for col in data_df.columns:
        if col != 'Year':  # Skip Year since it's already the index
            try:
                data_df[col] = pd.to_numeric(data_df[col], errors='coerce')
            except (TypeError, ValueError):
                # If conversion fails, skip this column
                continue
    
    return data_df

def get_all_countries():
    """Get list of all countries available in the dataset."""
    df = load_sheet('T6 Wine production')
    countries = df.iloc[1].tolist()[1:]  # Skip first NaN column
    return [c for c in countries if pd.notna(c)]

def get_regional_groups():
    """Define regional groupings for analysis."""
    return {
        'Western Europe': ['France', 'Italy', 'Portugal', 'Spain', 'Austria', 'Bel-Lux', 
                          'Denmark', 'Finland', 'Germany', 'Greece', 'Ireland', 'Netherlands',
                          'Sweden', 'Switzerland', 'United Kingdom', 'Other WEM'],
        'Eastern Europe & Central Asia': ['Bulgaria', 'Croatia', 'Georgia', 'Hungary', 
                                         'Moldova', 'Romania', 'Russia', 'Ukraine', 'Other ECA'],
        'Americas': ['Argentina', 'Brazil', 'Chile', 'Mexico', 'Uruguay', 'Other LAC', 
                    'Canada', 'United States'],
        'Asia Pacific': ['Australia', 'New Zealand', 'China', 'Hong Kong', 'India', 'Japan',
                        'Korea', 'Malaysia', 'Philippines', 'Singapore', 'Taiwan', 'Thailand',
                        'Other Asia Pacific'],
        'Africa & Middle East': ['Algeria', 'Morocco', 'South Africa', 'Tunisia', 'Turkey', 'Other AME'],
        'Transition Economies': ['Bulgaria', 'Croatia', 'Georgia', 'Hungary', 'Moldova', 
                                'Romania', 'Russia', 'Ukraine']
    }

def calculate_regional_totals(df, regions):
    """Calculate regional totals from country data."""
    regional_df = pd.DataFrame(index=df.index)
    
    for region, countries in regions.items():
        available_countries = [c for c in countries if c in df.columns]
        if available_countries:
            regional_df[region] = df[available_countries].sum(axis=1)
    
    return regional_df

# Load main data tables
@st.cache_data
def load_all_data():
    """Load all key data tables."""
    tables = {
        'vine_area': process_table('T1', 'T1 Vine area'),
        'wine_production': process_table('T6', 'T6 Wine production'),
        'wine_consumption': process_table('T34', 'T34 Wine consumption vol'),
        'population': process_table('T58', 'T58 Population'),
        'gdp': process_table('T61', 'T61 Real GDP'),
        'wine_exports_vol': process_table('T10', 'T10 Wine export vol'),
        'wine_imports_vol': process_table('T15', 'T15 Wine import vol'),
        'wine_exports_value': process_table('T21', 'T21 Wine export value'),
        'wine_imports_value': process_table('T25', 'T25 Wine import value'),
        'share_world_production': process_table('T7', 'T7 % world wine prodn'),
        'consumption_per_capita': process_table('T38', 'T38 Wine consumption per capita'),
        'comparative_advantage': process_table('T31', 'T31 Comparative advantage'),
    }
    return tables

# Main application
def main():
    # Header
    st.markdown('<h1 class="main-header">🍷 Global Wine Markets Analysis Dashboard</h1>', 
                unsafe_allow_html=True)
    st.markdown("""
    **Comprehensive analysis of global wine markets from 1835 to 2024**
    
    *Data Source: Annual Database of Global Wine Markets by Kym Anderson and Vicente Pinilla*
    *Wine Economics Research Centre, University of Adelaide*
    """)
    
    st.divider()
    
    # Load data
    with st.spinner("Loading comprehensive wine market database..."):
        tables = load_all_data()
        countries = get_all_countries()
        regions = get_regional_groups()
    
    # Sidebar navigation
    st.sidebar.header("📊 Navigation")
    analysis_type = st.sidebar.selectbox(
        "Select Analysis Type",
        ["Overview & Key Metrics",
         "Production Analysis",
         "Trade Analysis (Exports/Imports)",
         "Consumption Patterns",
         "Vineyard Area & Agricultural Land Use",
         "Regional Economic Analysis",
         "Comparative Advantage & Specialization",
         "Time Series Trends",
         "Country Comparison Tool"]
    )
    
    st.sidebar.divider()
    
    # Country and Region selectors
    st.sidebar.subheader("🌍 Filters")
    selected_countries = st.sidebar.multiselect(
        "Select Countries",
        countries,
        default=['France', 'Italy', 'Spain', 'United States', 'Australia']
    )
    
    selected_region = st.sidebar.selectbox(
        "Select Region for Aggregation",
        list(regions.keys()) + ['All Regions']
    )
    
    # Year range selector
    all_years = tables['wine_production'].index.dropna().astype(int)
    min_year, max_year = int(all_years.min()), int(all_years.max())
    year_range = st.sidebar.slider(
        "Year Range",
        min_year, max_year,
        (1850, 2020)
    )
    
    st.sidebar.divider()
    st.sidebar.info(f"""
    **Database Coverage:**
    - Years: {min_year} - {max_year}
    - Countries: {len(countries)}
    - Variables: 96+ tables
    """)
    
    # Main content based on selection
    if analysis_type == "Overview & Key Metrics":
        show_overview(tables, countries, regions, selected_countries, selected_region, year_range)
    elif analysis_type == "Production Analysis":
        show_production_analysis(tables, countries, regions, selected_countries, selected_region, year_range)
    elif analysis_type == "Trade Analysis (Exports/Imports)":
        show_trade_analysis(tables, countries, regions, selected_countries, selected_region, year_range)
    elif analysis_type == "Consumption Patterns":
        show_consumption_analysis(tables, countries, regions, selected_countries, selected_region, year_range)
    elif analysis_type == "Vineyard Area & Agricultural Land Use":
        show_vineyard_analysis(tables, countries, regions, selected_countries, selected_region, year_range)
    elif analysis_type == "Regional Economic Analysis":
        show_regional_economic_analysis(tables, countries, regions, selected_countries, selected_region, year_range)
    elif analysis_type == "Comparative Advantage & Specialization":
        show_comparative_advantage(tables, countries, regions, selected_countries, selected_region, year_range)
    elif analysis_type == "Time Series Trends":
        show_time_series_trends(tables, countries, regions, selected_countries, selected_region, year_range)
    elif analysis_type == "Country Comparison Tool":
        show_country_comparison(tables, countries, regions, selected_countries, selected_region, year_range)


def show_overview(tables, countries, regions, selected_countries, selected_region, year_range):
    """Display overview dashboard with key metrics."""
    st.markdown('<h2 class="sub-header">📈 Overview & Key Metrics</h2>', unsafe_allow_html=True)
    
    wine_prod = tables['wine_production']
    vine_area = tables['vine_area']
    consumption = tables['wine_consumption']
    
    # Filter by year range
    mask = (wine_prod.index >= year_range[0]) & (wine_prod.index <= year_range[1])
    
    # Latest year metrics
    latest_year = wine_prod[mask].index.max()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        world_prod_latest = wine_prod.loc[latest_year, 'World'] if 'World' in wine_prod.columns else wine_prod.loc[latest_year].sum()
        st.metric(
            label=f"Global Wine Production ({int(latest_year)})",
            value=f"{world_prod_latest/1e6:.1f} ML",
            help="Megaliters (millions of liters)"
        )
    
    with col2:
        world_area_latest = vine_area.loc[latest_year, 'World'] if 'World' in vine_area.columns else vine_area.loc[latest_year].sum()
        st.metric(
            label=f"Global Vineyard Area ({int(latest_year)})",
            value=f"{world_area_latest/1e3:.1f} K ha",
            help="Thousands of hectares"
        )
    
    with col3:
        world_cons_latest = consumption.loc[latest_year, 'World'] if 'World' in consumption.columns else consumption.loc[latest_year].sum()
        st.metric(
            label=f"Global Wine Consumption ({int(latest_year)})",
            value=f"{world_cons_latest/1e6:.1f} ML",
            help="Megaliters (millions of liters)"
        )
    
    with col4:
        if len(selected_countries) > 0:
            top_producer = selected_countries[0]
            prod_share = wine_prod.loc[latest_year, top_producer] / wine_prod.loc[latest_year, 'World'] * 100 if 'World' in wine_prod.columns else 0
            st.metric(
                label=f"{top_producer} Share of Production",
                value=f"{prod_share:.1f}%",
                delta=f"vs global avg"
            )
    
    st.divider()
    
    # World maps
    st.markdown("### 🗺️ Global Distribution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = create_choropleth(wine_prod, latest_year, 'Wine Production Volume (ML)', selected_countries)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = create_choropleth(vine_area, latest_year, 'Vineyard Area (ha)', selected_countries)
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Top producers/consumers
    st.markdown("### 🏆 Top Producers and Consumers")
    
    col1, col2 = st.columns(2)
    
    with col1:
        top_n = 10
        exclude_cols = ['World', 'Unnamed: 0']
        available_cols = [c for c in wine_prod.columns if c not in exclude_cols and pd.notna(c)]
        
        latest_data = wine_prod.loc[latest_year, available_cols].dropna()
        top_producers = latest_data.nlargest(top_n)
        
        fig = px.bar(
            x=top_producers.values/1e6,
            y=top_producers.index,
            orientation='h',
            title=f"Top {top_n} Wine Producers ({int(latest_year)})",
            labels={'x': 'Production Volume (ML)', 'y': 'Country'},
            color=top_producers.values,
            color_continuous_scale='YlOrRd'
        )
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        available_cols_cons = [c for c in consumption.columns if c not in exclude_cols and pd.notna(c)]
        latest_cons = consumption.loc[latest_year, available_cols_cons].dropna()
        top_consumers = latest_cons.nlargest(top_n)
        
        fig = px.bar(
            x=top_consumers.values/1e6,
            y=top_consumers.index,
            orientation='h',
            title=f"Top {top_n} Wine Consumers ({int(latest_year)})",
            labels={'x': 'Consumption Volume (ML)', 'y': 'Country'},
            color=top_consumers.values,
            color_continuous_scale='YlGnBu'
        )
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Expert Analysis Box
    st.markdown("""
    <div class="analysis-box">
    <h4>🎓 Level 1 Analysis: Descriptive Overview</h4>
    <p>
    The global wine industry has undergone significant transformation since 1835. Key observations include:
    </p>
    <ul>
    <li><strong>Production Concentration:</strong> Traditional European producers (France, Italy, Spain) have historically dominated global wine production, though New World producers have gained significant market share since the 1980s.</li>
    <li><strong>Consumption Shifts:</strong> Per capita consumption patterns reveal a shift from traditional wine-consuming countries to emerging markets, particularly in Asia and North America.</li>
    <li><strong>Vineyard Area Efficiency:</strong> Despite fluctuations in total vineyard area, productivity improvements through technology and viticultural practices have maintained or increased output.</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)


def create_choropleth(df, year, title, selected_countries):
    """Create a choropleth map for a given year."""
    # Get data for the year
    exclude_cols = ['World', 'Unnamed: 0']
    available_cols = [c for c in df.columns if c not in exclude_cols and pd.notna(c)]
    
    if year in df.index:
        year_data = df.loc[year, available_cols].dropna()
    else:
        # Find closest year
        closest_year = min(df.index, key=lambda x: abs(x - year))
        year_data = df.loc[closest_year, available_cols].dropna()
    
    # Create DataFrame for plotting
    plot_df = pd.DataFrame({
        'Country': year_data.index,
        'Value': year_data.values
    })
    
    fig = px.choropleth(
        plot_df,
        locations='Country',
        locationmode='country names',
        color='Value',
        color_continuous_scale='Reds',
        title=f"{title} - {int(year)}",
        hover_name='Country',
        hover_data={'Value': ':,.0f'}
    )
    fig.update_layout(
        geo=dict(showframe=False, projection_type='natural earth'),
        coloraxis_colorbar=dict(title=title.split('(')[0])
    )
    return fig


def show_production_analysis(tables, countries, regions, selected_countries, selected_region, year_range):
    """Display wine production analysis."""
    st.markdown('<h2 class="sub-header">🍇 Wine Production Analysis</h2>', unsafe_allow_html=True)
    
    wine_prod = tables['wine_production']
    share_prod = tables['share_world_production']
    
    # Filter by year range
    mask = (wine_prod.index >= year_range[0]) & (wine_prod.index <= year_range[1])
    wine_prod_filtered = wine_prod[mask]
    
    # Time series chart
    st.markdown("### Historical Production Trends")
    
    if selected_countries:
        fig = go.Figure()
        for country in selected_countries[:8]:  # Limit to 8 countries for clarity
            if country in wine_prod_filtered.columns:
                fig.add_trace(go.Scatter(
                    x=wine_prod_filtered.index,
                    y=wine_prod_filtered[country]/1e6,
                    mode='lines',
                    name=country,
                    line=dict(width=2)
                ))
        
        fig.update_layout(
            title='Wine Production Volume by Country (ML)',
            xaxis_title='Year',
            yaxis_title='Volume (Megaliters)',
            hovermode='x unified',
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Regional analysis
    if selected_region != 'All Regions':
        st.markdown(f"### {selected_region} Production Analysis")
        regional_countries = regions.get(selected_region, [])
        available_countries = [c for c in regional_countries if c in wine_prod.columns]
        
        if available_countries:
            regional_prod = wine_prod_filtered[available_countries].sum(axis=1)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=regional_prod.index,
                y=regional_prod.values/1e6,
                mode='lines+markers',
                name=f'{selected_region} Total',
                line=dict(width=3, color='#722F37')
            ))
            
            fig.update_layout(
                title=f'{selected_region} - Total Wine Production',
                xaxis_title='Year',
                yaxis_title='Volume (Megaliters)',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Market share evolution
    st.markdown("### Evolution of Global Market Share")
    
    if share_prod is not None:
        share_mask = (share_prod.index >= year_range[0]) & (share_prod.index <= year_range[1])
        share_filtered = share_prod[share_mask]
        
        if selected_countries:
            fig = go.Figure()
            for country in selected_countries[:6]:
                if country in share_filtered.columns:
                    fig.add_trace(go.Scatter(
                        x=share_filtered.index,
                        y=share_filtered[country],
                        mode='lines',
                        name=country,
                        stackgroup='one'
                    ))
            
            fig.update_layout(
                title='Share of World Wine Production (%)',
                xaxis_title='Year',
                yaxis_title='Percentage',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Production volatility analysis
    st.markdown("### Production Volatility Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if selected_countries:
            recent_data = wine_prod.loc[year_range[1]-10:year_range[1], selected_countries]
            volatility = recent_data.std() / recent_data.mean() * 100
            
            fig = px.bar(
                x=volatility.index,
                y=volatility.values,
                title='Production Coefficient of Variation (Last 10 Years)',
                labels={'x': 'Country', 'y': 'CV (%)'}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("""
        <div class="analysis-box">
        <h4>🎓 Level 2 Analysis: Production Economics</h4>
        <p>
        <strong>Key Production Insights:</strong>
        </p>
        <ul>
        <li><strong>Climatic Vulnerability:</strong> Wine production exhibits significant inter-annual volatility due to weather conditions, particularly in traditional European regions.</li>
        <li><strong>Technological Adaptation:</strong> New World producers have demonstrated more stable production through irrigation and modern viticultural techniques.</li>
        <li><strong>Policy Impacts:</strong> EU wine policy reforms (particularly 2008 grubbing-up scheme) significantly affected European production capacity.</li>
        <li><strong>Market Dynamics:</strong> Production shifts reflect both supply-side factors (climate, policy) and demand-side pressures (changing consumption patterns).</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)


def show_trade_analysis(tables, countries, regions, selected_countries, selected_region, year_range):
    """Display trade analysis (exports and imports)."""
    st.markdown('<h2 class="sub-header">🚢 Trade Analysis: Exports & Imports</h2>', unsafe_allow_html=True)
    
    exports_vol = tables['wine_exports_vol']
    imports_vol = tables['wine_imports_vol']
    exports_val = tables['wine_exports_value']
    imports_val = tables['wine_imports_value']
    
    # Filter by year range
    mask = (exports_vol.index >= year_range[0]) & (exports_vol.index <= year_range[1])
    
    st.markdown("### Trade Volume Trends")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if selected_countries:
            fig = go.Figure()
            for country in selected_countries[:6]:
                if country in exports_vol.columns:
                    fig.add_trace(go.Scatter(
                        x=exports_vol.loc[mask].index,
                        y=exports_vol.loc[mask][country]/1e6,
                        mode='lines',
                        name=country
                    ))
            
            fig.update_layout(
                title='Wine Export Volume by Country (ML)',
                xaxis_title='Year',
                yaxis_title='Volume (Megaliters)',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if selected_countries:
            fig = go.Figure()
            for country in selected_countries[:6]:
                if country in imports_vol.columns:
                    fig.add_trace(go.Scatter(
                        x=imports_vol.loc[mask].index,
                        y=imports_vol.loc[mask][country]/1e6,
                        mode='lines',
                        name=country
                    ))
            
            fig.update_layout(
                title='Wine Import Volume by Country (ML)',
                xaxis_title='Year',
                yaxis_title='Volume (Megaliters)',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Unit values (price analysis)
    st.markdown("### Unit Value Analysis (Price per Liter)")
    
    if selected_countries:
        col1, col2 = st.columns(2)
        
        with col1:
            # Calculate export unit values
            export_unit_value = exports_val / exports_vol * 1000  # Convert to $/L or similar
            recent_year = year_range[1]
            
            if recent_year in export_unit_value.index:
                uv_data = export_unit_value.loc[recent_year, selected_countries].dropna()
                
                fig = px.bar(
                    x=uv_data.index,
                    y=uv_data.values,
                    title=f'Export Unit Values by Country ({int(recent_year)})',
                    labels={'x': 'Country', 'y': 'Unit Value'}
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Calculate import unit values
            import_unit_value = imports_val / imports_vol * 1000
            recent_year = year_range[1]
            
            if recent_year in import_unit_value.index:
                uv_data = import_unit_value.loc[recent_year, selected_countries].dropna()
                
                fig = px.bar(
                    x=uv_data.index,
                    y=uv_data.values,
                    title=f'Import Unit Values by Country ({int(recent_year)})',
                    labels={'x': 'Country', 'y': 'Unit Value'}
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
    
    # Trade balance
    st.markdown("### Net Trade Position")
    
    if selected_countries:
        net_trade = exports_vol.loc[mask] - imports_vol.loc[mask]
        
        fig = go.Figure()
        for country in selected_countries[:6]:
            if country in net_trade.columns:
                fig.add_trace(go.Scatter(
                    x=net_trade.index,
                    y=net_trade[country]/1e6,
                    mode='lines',
                    name=country
                ))
        
        fig.add_hline(y=0, line_dash="dash", line_color="gray")
        fig.update_layout(
            title='Net Wine Trade Balance (Exports - Imports) in ML',
            xaxis_title='Year',
            yaxis_title='Net Trade Volume (Megaliters)',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Expert analysis
    st.markdown("""
    <div class="analysis-box">
    <h4>🎓 Level 3 Analysis: Trade Economics & Regional Integration</h4>
    <p>
    <strong>Trade Pattern Insights:</strong>
    </p>
    <ul>
    <li><strong>Intra-industry Trade:</strong> Significant two-way trade in wine reflects product differentiation and consumer preference diversity rather than simple comparative advantage.</li>
    <li><strong>Quality Segmentation:</strong> Unit value differences reveal quality segmentation in global markets, with Old World producers often commanding premium prices.</li>
    <li><strong>Regional Trade Agreements:</strong> EU integration facilitated intra-European wine trade while external tariffs protected regional producers.</li>
    <li><strong>Emerging Exporters:</strong> Southern Hemisphere producers (Australia, Chile, New Zealand) successfully penetrated Northern Hemisphere markets through competitive pricing and quality improvements.</li>
    <li><strong>Exchange Rate Effects:</strong> Wine trade flows are sensitive to real exchange rate movements, affecting competitiveness of exporting nations.</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)


def show_consumption_analysis(tables, countries, regions, selected_countries, selected_region, year_range):
    """Display consumption pattern analysis."""
    st.markdown('<h2 class="sub-header">🥂 Consumption Patterns Analysis</h2>', unsafe_allow_html=True)
    
    consumption = tables['wine_consumption']
    consumption_pc = tables['consumption_per_capita']
    population = tables['population']
    
    # Filter by year range
    mask = (consumption.index >= year_range[0]) & (consumption.index <= year_range[1])
    
    st.markdown("### Total Consumption Trends")
    
    if selected_countries:
        fig = go.Figure()
        for country in selected_countries[:8]:
            if country in consumption.columns:
                fig.add_trace(go.Scatter(
                    x=consumption.loc[mask].index,
                    y=consumption.loc[mask][country]/1e6,
                    mode='lines',
                    name=country
                ))
        
        fig.update_layout(
            title='Wine Consumption Volume by Country (ML)',
            xaxis_title='Year',
            yaxis_title='Volume (Megaliters)',
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Per capita consumption
    st.markdown("### Per Capita Consumption Analysis")
    
    if consumption_pc is not None:
        pc_mask = (consumption_pc.index >= year_range[0]) & (consumption_pc.index <= year_range[1])
        
        col1, col2 = st.columns(2)
        
        with col1:
            if selected_countries:
                fig = go.Figure()
                for country in selected_countries[:6]:
                    if country in consumption_pc.columns:
                        fig.add_trace(go.Scatter(
                            x=consumption_pc.loc[pc_mask].index,
                            y=consumption_pc.loc[pc_mask][country],
                            mode='lines',
                            name=country
                        ))
                
                fig.update_layout(
                    title='Wine Consumption Per Capita (Liters)',
                    xaxis_title='Year',
                    yaxis_title='Liters per Capita',
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Latest year comparison
            latest_year = consumption_pc.loc[pc_mask].index.max()
            available_cols = [c for c in consumption_pc.columns if c in selected_countries and pd.notna(c)]
            
            if available_cols and latest_year in consumption_pc.index:
                latest_pc = consumption_pc.loc[latest_year, available_cols].dropna().nlargest(15)
                
                fig = px.bar(
                    x=latest_pc.values,
                    y=latest_pc.index,
                    orientation='h',
                    title=f'Per Capita Consumption Ranking ({int(latest_year)})',
                    labels={'x': 'Liters per Capita', 'y': 'Country'}
                )
                fig.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
    
    # Consumption intensity
    st.markdown("### Consumption Intensity Index")
    
    st.markdown("""
    <div class="analysis-box">
    <h4>🎓 Level 4 Analysis: Consumption Economics & Cultural Factors</h4>
    <p>
    <strong>Consumption Pattern Insights:</strong>
    </p>
    <ul>
    <li><strong>Convergence vs Divergence:</strong> Traditional wine-consuming countries show declining per capita consumption while new markets exhibit growth, suggesting convergence in global consumption patterns.</li>
    <li><strong>Income Elasticity:</strong> Wine consumption demonstrates varying income elasticity across development stages - luxury good in emerging markets, necessity/inferior good in mature markets.</li>
    <li><strong>Cultural Persistence:</strong> Despite globalization, Mediterranean countries maintain higher baseline consumption reflecting deep-rooted cultural practices.</li>
    <li><strong>Demographic Transitions:</strong> Aging populations in traditional markets contrast with younger demographics in emerging markets, affecting long-term consumption trajectories.</li>
    <li><strong>Health & Policy Effects:</strong> Public health campaigns and alcohol policies have measurably impacted consumption levels, particularly in Northern Europe.</li>
    <li><strong>Substitution Effects:</strong> Competition from beer, spirits, and non-alcoholic beverages affects wine's share of total alcohol consumption.</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)


def show_vineyard_analysis(tables, countries, regions, selected_countries, selected_region, year_range):
    """Display vineyard area and agricultural land use analysis."""
    st.markdown('<h2 class="sub-header">🌱 Vineyard Area & Agricultural Land Use</h2>', unsafe_allow_html=True)
    
    vine_area = tables['vine_area']
    
    # Filter by year range
    mask = (vine_area.index >= year_range[0]) & (vine_area.index <= year_range[1])
    
    st.markdown("### Vineyard Area Trends")
    
    if selected_countries:
        fig = go.Figure()
        for country in selected_countries[:8]:
            if country in vine_area.columns:
                fig.add_trace(go.Scatter(
                    x=vine_area.loc[mask].index,
                    y=vine_area.loc[mask][country]/1e3,
                    mode='lines',
                    name=country
                ))
        
        fig.update_layout(
            title='Vineyard Area by Country (Thousands of Hectares)',
            xaxis_title='Year',
            yaxis_title='Area (K hectares)',
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Productivity analysis (production per hectare)
    st.markdown("### Vineyard Productivity (Yield per Hectare)")
    
    wine_prod = tables['wine_production']
    
    if selected_countries:
        productivity = wine_prod.loc[mask] / vine_area.loc[mask] * 1000  # Liters per hectare
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = go.Figure()
            for country in selected_countries[:6]:
                if country in productivity.columns:
                    fig.add_trace(go.Scatter(
                        x=productivity.index,
                        y=productivity[country],
                        mode='lines',
                        name=country
                    ))
            
            fig.update_layout(
                title='Wine Yield (Liters per Hectare)',
                xaxis_title='Year',
                yaxis_title='Yield (L/ha)',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Latest year comparison
            latest_year = productivity.index.max()
            prod_latest = productivity.loc[latest_year, selected_countries].dropna()
            
            fig = px.bar(
                x=prod_latest.index,
                y=prod_latest.values,
                title=f'Yield Comparison ({int(latest_year)})',
                labels={'x': 'Country', 'y': 'Yield (L/ha)'}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    # Area efficiency
    st.markdown("### Vineyard Area per Million USD GDP")
    
    st.markdown("""
    <div class="analysis-box">
    <h4>🎓 Level 5 Analysis: Agricultural Economics & Structural Transformation</h4>
    <p>
    <strong>Vineyard & Land Use Insights:</strong>
    </p>
    <ul>
    <li><strong>Structural Change:</strong> Declining vineyard area in developed economies reflects broader agricultural transformation and urbanization pressures.</li>
    <li><strong>Intensification vs Extensification:</strong> Yield improvements through technology (irrigation, clonal selection, precision viticulture) have offset area reductions.</li>
    <li><strong>Comparative Land Use:</strong> Vineyard area relative to total agricultural land reveals specialization patterns and opportunity costs in land allocation.</li>
    <li><strong>Policy Distortions:</strong> Planting rights regimes and grubbing-up schemes created artificial constraints affecting optimal land use patterns.</li>
    <li><strong>Climate Change Adaptation:</strong> Geographic shifts in vineyard locations signal adaptation to changing climatic conditions, with potential northward expansion.</li>
    <li><strong>Economic Development Pathway:</strong> Vineyard area per GDP demonstrates transition from extensive to intensive production systems as economies develop.</li>
    <li><strong>Terroir vs Technology:</strong> Tension between traditional terroir-based systems and technology-driven production models shapes regional competitiveness.</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)


def show_regional_economic_analysis(tables, countries, regions, selected_countries, selected_region, year_range):
    """Display regional economic analysis."""
    st.markdown('<h2 class="sub-header">🌍 Regional Economic Analysis</h2>', unsafe_allow_html=True)
    
    wine_prod = tables['wine_production']
    gdp = tables['gdp']
    population = tables['population']
    
    # Filter by year range
    mask = (wine_prod.index >= year_range[0]) & (wine_prod.index <= year_range[1])
    
    # Calculate regional aggregates
    st.markdown("### Regional Production Shares")
    
    regional_prod = calculate_regional_totals(wine_prod.loc[mask], regions)
    
    fig = go.Figure()
    for region in regional_prod.columns:
        fig.add_trace(go.Scatter(
            x=regional_prod.index,
            y=regional_prod[region]/1e6,
            mode='lines',
            name=region
        ))
    
    fig.update_layout(
        title='Wine Production by Region (ML)',
        xaxis_title='Year',
        yaxis_title='Volume (Megaliters)',
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Regional market share evolution
    st.markdown("### Evolution of Regional Market Shares")
    
    regional_total = regional_prod.sum(axis=1)
    
    fig = go.Figure()
    for region in regional_prod.columns:
        share = regional_prod[region] / regional_total * 100
        fig.add_trace(go.Scatter(
            x=share.index,
            y=share.values,
            mode='lines',
            name=region,
            stackgroup='one'
        ))
    
    fig.update_layout(
        title='Regional Share of Global Wine Production (%)',
        xaxis_title='Year',
        yaxis_title='Percentage',
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # GDP correlation
    st.markdown("### Wine Production vs Economic Development")
    
    if selected_region != 'All Regions':
        st.markdown(f"#### {selected_region} Analysis")
        
        regional_countries = regions.get(selected_region, [])
        available_countries = [c for c in regional_countries if c in wine_prod.columns and c in gdp.columns]
        
        if available_countries:
            # Scatter plot of production vs GDP
            latest_year = min(year_range[1], 2020)
            
            if latest_year in wine_prod.index and latest_year in gdp.index:
                prod_data = wine_prod.loc[latest_year, available_countries]
                gdp_data = gdp.loc[latest_year, available_countries]
                
                scatter_df = pd.DataFrame({
                    'Country': available_countries,
                    'Production': prod_data.values,
                    'GDP': gdp_data.values
                }).dropna()
                
                fig = px.scatter(
                    scatter_df,
                    x='GDP',
                    y='Production',
                    size='Production',
                    hover_name='Country',
                    title=f'Wine Production vs GDP ({int(latest_year)})',
                    labels={'GDP': 'Real GDP', 'Production': 'Wine Production (KL)'},
                    log_x=True,
                    log_y=True
                )
                st.plotly_chart(fig, use_container_width=True)
    
    # Regional specialization index
    st.markdown("### Regional Specialization Over Time")
    
    st.markdown("""
    <div class="analysis-box">
    <h4>🎓 Integrated Regional Economic Analysis</h4>
    <p>
    <strong>Five-Level Analytical Framework Applied:</strong>
    </p>
    <ol>
    <li><strong>Descriptive (Level 1):</strong> Document regional production, consumption, and trade patterns over time.</li>
    <li><strong>Production Economics (Level 2):</strong> Analyze factor productivity, technological change, and cost structures across regions.</li>
    <li><strong>Trade Economics (Level 3):</strong> Examine comparative advantage, intra-industry trade, and regional integration effects.</li>
    <li><strong>Consumption Economics (Level 4):</strong> Assess income elasticities, cultural factors, and demographic influences on regional demand.</li>
    <li><strong>Structural Transformation (Level 5):</strong> Evaluate wine sector's role in broader agricultural and economic development pathways.</li>
    </ol>
    <p><strong>Key Regional Insights:</strong></p>
    <ul>
    <li><strong>Western Europe:</strong> Mature market with declining consumption but sustained premium production focus.</li>
    <li><strong>New World (Americas, Oceania):</strong> Dynamic exporters with technology-driven production and marketing innovation.</li>
    <li><strong>Transition Economies:</strong> Restructuring from planned to market systems with varying success in regaining historical market positions.</li>
    <li><strong>Asia Pacific:</strong> Emerging consumption powerhouse with Japan and China leading import growth.</li>
    <li><strong>Africa:</strong> South Africa as established exporter; North African traditional producers facing domestic market challenges.</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)


def show_comparative_advantage(tables, countries, regions, selected_countries, selected_region, year_range):
    """Display comparative advantage and specialization analysis."""
    st.markdown('<h2 class="sub-header">⚖️ Comparative Advantage & Specialization</h2>', unsafe_allow_html=True)
    
    ca_table = tables.get('comparative_advantage')
    wine_prod = tables['wine_production']
    
    if ca_table is not None:
        # Filter by year range
        mask = (ca_table.index >= year_range[0]) & (ca_table.index <= year_range[1])
        ca_filtered = ca_table[mask]
        
        st.markdown("### Revealed Comparative Advantage (RCA) Index")
        st.markdown("*RCA > 1 indicates comparative advantage in wine production*")
        
        if selected_countries:
            fig = go.Figure()
            for country in selected_countries[:8]:
                if country in ca_filtered.columns:
                    fig.add_trace(go.Scatter(
                        x=ca_filtered.index,
                        y=ca_filtered[country],
                        mode='lines',
                        name=country
                    ))
            
            fig.add_hline(y=1, line_dash="dash", line_color="red", annotation_text="RCA = 1 (No CA)")
            fig.update_layout(
                title='Revealed Comparative Advantage in Wine Production',
                xaxis_title='Year',
                yaxis_title='RCA Index',
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Latest year RCA ranking
        st.markdown("### Current Comparative Advantage Rankings")
        
        latest_year = ca_filtered.index.max()
        available_cols = [c for c in ca_filtered.columns if pd.notna(c) and c not in ['World']]
        
        if available_cols and latest_year in ca_filtered.index:
            latest_ca = ca_filtered.loc[latest_year, available_cols].dropna().nlargest(20)
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(
                    x=latest_ca.index,
                    y=latest_ca.values,
                    title=f'RCA Rankings ({int(latest_year)})',
                    labels={'x': 'Country', 'y': 'RCA Index'}
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("""
                **RCA Interpretation:**
                - RCA > 2: Strong comparative advantage
                - 1 < RCA < 2: Moderate comparative advantage  
                - RCA < 1: Comparative disadvantage
                - RCA < 0.5: Strong comparative disadvantage
                """)
    
    # Trade specialization
    st.markdown("### Trade Specialization Patterns")
    
    exports_vol = tables['wine_exports_vol']
    imports_vol = tables['wine_imports_vol']
    
    if selected_countries:
        mask = (exports_vol.index >= year_range[0]) & (exports_vol.index <= year_range[1])
        
        # Calculate export orientation
        export_orientation = exports_vol.loc[mask] / wine_prod.loc[mask] * 100
        
        fig = go.Figure()
        for country in selected_countries[:6]:
            if country in export_orientation.columns:
                fig.add_trace(go.Scatter(
                    x=export_orientation.index,
                    y=export_orientation[country],
                    mode='lines',
                    name=country
                ))
        
        fig.update_layout(
            title='Export Orientation (% of Production Exported)',
            xaxis_title='Year',
            yaxis_title='Percentage',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("""
    <div class="analysis-box">
    <h4>🎓 Comparative Advantage Analysis Framework</h4>
    <p>
    <strong>Theoretical Foundations:</strong>
    </p>
    <ul>
    <li><strong>Heckscher-Ohlin Framework:</strong> Wine production advantages reflect factor endowments (climate, land suitability, labor skills).</li>
    <li><strong>Specific Factors Model:</strong> Vineyard land as sector-specific factor creates persistent advantage patterns.</li>
    <li><strong>Dynamic Comparative Advantage:</strong> Technology transfer and investment can shift comparative advantage over time.</li>
    <li><strong>Quality Upgrading:</strong> Movement up quality ladder allows producers to maintain competitiveness despite cost disadvantages.</li>
    <li><strong>Geographical Indications:</strong> Institutional protection of terroir-based advantages affects competitive dynamics.</li>
    </ul>
    <p><strong>Empirical Patterns:</strong></p>
    <ul>
    <li>Mediterranean countries maintain strong RCA despite higher costs due to reputation and quality perception</li>
    <li>Southern Hemisphere producers developed RCA through scale, technology, and marketing</li>
    <li>Small specialized producers (e.g., New Zealand) achieve high RCA through niche positioning</li>
    <li>Large domestic market countries (US, Germany) show lower RCA but significant absolute trade volumes</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)


def show_time_series_trends(tables, countries, regions, selected_countries, selected_region, year_range):
    """Display comprehensive time series trends."""
    st.markdown('<h2 class="sub-header">📊 Long-Term Time Series Trends</h2>', unsafe_allow_html=True)
    
    wine_prod = tables['wine_production']
    consumption = tables['wine_consumption']
    vine_area = tables['vine_area']
    
    # Extended time period selector
    st.markdown("### Select Variables for Time Series Analysis")
    
    var1 = st.selectbox("Primary Variable", 
                       ['Wine Production', 'Consumption', 'Vineyard Area', 'Exports', 'Imports'])
    var2 = st.selectbox("Secondary Variable (Optional)",
                       ['None', 'Wine Production', 'Consumption', 'Vineyard Area', 'Exports', 'Imports'])
    
    # Create multi-panel figure
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                       vertical_spacing=0.05,
                       subplot_titles=(f'{var1} Trends', f'{var1} - Growth Rates'))
    
    # Primary variable
    if var1 == 'Wine Production':
        data = wine_prod
        unit = 'ML'
        divisor = 1e6
    elif var1 == 'Consumption':
        data = consumption
        unit = 'ML'
        divisor = 1e6
    elif var1 == 'Vineyard Area':
        data = vine_area
        unit = 'K ha'
        divisor = 1e3
    elif var1 == 'Exports':
        data = tables['wine_exports_vol']
        unit = 'ML'
        divisor = 1e6
    elif var1 == 'Imports':
        data = tables['wine_imports_vol']
        unit = 'ML'
        divisor = 1e6
    
    mask = (data.index >= year_range[0]) & (data.index <= year_range[1])
    
    colors = px.colors.qualitative.Set1
    
    for i, country in enumerate(selected_countries[:6]):
        if country in data.columns:
            fig.add_trace(
                go.Scatter(x=data.loc[mask].index, y=data.loc[mask][country]/divisor,
                          mode='lines', name=country, line=dict(color=colors[i % len(colors)])),
                row=1, col=1
            )
            
            # Calculate growth rates
            growth_rate = data.loc[mask][country].pct_change() * 100
            fig.add_trace(
                go.Scatter(x=data.loc[mask].index[1:], y=growth_rate.dropna(),
                          mode='lines', name=f'{country} Growth', 
                          line=dict(color=colors[i % len(colors)], dash='dash'),
                          showlegend=False),
                row=2, col=1
            )
    
    fig.update_layout(height=700, title_text=f'{var1} Analysis for Selected Countries',
                     hovermode='x unified')
    fig.update_xaxes(title_text='Year', row=2, col=1)
    fig.update_yaxes(title_text=unit, row=1, col=1)
    fig.update_yaxes(title_text='Growth Rate (%)', row=2, col=1)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Structural break analysis
    st.markdown("### Structural Break Detection")
    
    st.markdown("""
    **Notable Structural Breaks in Global Wine Markets:**
    - **1870s-1890s**: Phylloxera crisis devastated European vineyards
    - **1920s-1930s**: Prohibition effects and Great Depression
    - **1970s-1980s**: New World emergence and quality revolution
    - **2000s**: EU wine policy reforms and globalization acceleration
    - **2008-2009**: Global financial crisis impacts
    """)
    
    # Rolling statistics
    st.markdown("### Rolling Statistics (10-Year Window)")
    
    if selected_countries:
        rolling_window = 10
        rolling_mean = data.loc[mask][selected_countries].rolling(window=rolling_window).mean()
        rolling_std = data.loc[mask][selected_countries].rolling(window=rolling_window).std()
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = go.Figure()
            for country in selected_countries[:4]:
                if country in rolling_mean.columns:
                    fig.add_trace(go.Scatter(
                        x=rolling_mean.index,
                        y=rolling_mean[country]/divisor,
                        mode='lines',
                        name=f'{country} Mean'
                    ))
            
            fig.update_layout(
                title=f'{rolling_window}-Year Rolling Mean',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = go.Figure()
            for country in selected_countries[:4]:
                if country in rolling_std.columns:
                    fig.add_trace(go.Scatter(
                        x=rolling_std.index,
                        y=rolling_std[country]/divisor,
                        mode='lines',
                        name=f'{country} Std Dev'
                    ))
            
            fig.update_layout(
                title=f'{rolling_window}-Year Rolling Standard Deviation',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)


def show_country_comparison(tables, countries, regions, selected_countries, selected_region, year_range):
    """Display country comparison tool."""
    st.markdown('<h2 class="sub-header">🔍 Country Comparison Tool</h2>', unsafe_allow_html=True)
    
    # Allow user to select specific countries for detailed comparison
    compare_countries = st.multiselect(
        "Select Countries for Detailed Comparison",
        countries,
        default=['France', 'Italy', 'Spain', 'United States'] if len(selected_countries) < 2 else selected_countries[:4],
        max_selections=6
    )
    
    if len(compare_countries) >= 2:
        # Create comparison dashboard
        wine_prod = tables['wine_production']
        consumption = tables['wine_consumption']
        vine_area = tables['vine_area']
        exports_vol = tables['wine_exports_vol']
        
        latest_year = min(year_range[1], 2020)
        
        # Key metrics comparison table
        st.markdown("### Key Metrics Comparison")
        
        metrics_data = []
        for country in compare_countries:
            if latest_year in wine_prod.index:
                try:
                    row = {
                        'Country': country,
                        'Production (ML)': wine_prod.loc[latest_year, country] / 1e6 if country in wine_prod.columns else None,
                        'Consumption (ML)': consumption.loc[latest_year, country] / 1e6 if country in consumption.columns else None,
                        'Vineyard Area (K ha)': vine_area.loc[latest_year, country] / 1e3 if country in vine_area.columns else None,
                        'Exports (ML)': exports_vol.loc[latest_year, country] / 1e6 if country in exports_vol.columns else None,
                    }
                    metrics_data.append(row)
                except:
                    pass
        
        if metrics_data:
            comparison_df = pd.DataFrame(metrics_data)
            st.dataframe(comparison_df.style.format('{:.2f}'), use_container_width=True)
        
        # Radar chart for multi-dimensional comparison
        st.markdown("### Multi-Dimensional Country Comparison")
        
        categories = ['Production', 'Consumption', 'Exports', 'Vineyard Area']
        
        fig = go.Figure()
        
        for country in compare_countries:
            values = []
            for cat in categories:
                if cat == 'Production':
                    val = wine_prod.loc[latest_year, country] / 1e6 if country in wine_prod.columns else 0
                elif cat == 'Consumption':
                    val = consumption.loc[latest_year, country] / 1e6 if country in consumption.columns else 0
                elif cat == 'Exports':
                    val = exports_vol.loc[latest_year, country] / 1e6 if country in exports_vol.columns else 0
                elif cat == 'Vineyard Area':
                    val = vine_area.loc[latest_year, country] / 1e3 if country in vine_area.columns else 0
                values.append(val)
            
            # Normalize values for radar chart
            max_vals = [comparison_df[cat.replace(' (ML)', '').replace(' (K ha)', '')].max() for cat in categories]
            normalized_values = [v/m if m > 0 else 0 for v, m in zip(values, max_vals)]
            
            fig.add_trace(go.Scatterpolar(
                r=normalized_values,
                theta=categories,
                fill='toself',
                name=country
            ))
        
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 1.1])),
            showlegend=True,
            title=f'Normalized Country Comparison ({int(latest_year)})',
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Historical trajectory comparison
        st.markdown("### Historical Development Trajectories")
        
        metric = st.selectbox("Select Metric for Trajectory Comparison",
                             ['Wine Production', 'Consumption', 'Vineyard Area', 'Exports'])
        
        if metric == 'Wine Production':
            data = wine_prod
            divisor = 1e6
            unit = 'ML'
        elif metric == 'Consumption':
            data = consumption
            divisor = 1e6
            unit = 'ML'
        elif metric == 'Vineyard Area':
            data = vine_area
            divisor = 1e3
            unit = 'K ha'
        elif metric == 'Exports':
            data = exports_vol
            divisor = 1e6
            unit = 'ML'
        
        mask = (data.index >= year_range[0]) & (data.index <= year_range[1])
        
        fig = go.Figure()
        for country in compare_countries:
            if country in data.columns:
                fig.add_trace(go.Scatter(
                    x=data.loc[mask].index,
                    y=data.loc[mask][country] / divisor,
                    mode='lines+markers',
                    name=country,
                    marker=dict(size=6)
                ))
        
        fig.update_layout(
            title=f'{metric} Comparison Over Time',
            xaxis_title='Year',
            yaxis_title=unit,
            height=500,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Statistical summary
        st.markdown("### Statistical Summary")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Mean (Last Decade)**")
            for country in compare_countries:
                if country in data.columns:
                    mean_val = data.loc[year_range[1]-9:year_range[1], country].mean() / divisor
                    st.write(f"{country}: {mean_val:.2f} {unit}")
        
        with col2:
            st.markdown("**Growth Rate (CAGR, Last Decade)**")
            for country in compare_countries:
                if country in data.columns:
                    start_val = data.loc[year_range[1]-9, country]
                    end_val = data.loc[year_range[1], country]
                    if start_val > 0:
                        cagr = (end_val / start_val) ** (1/10) - 1
                        st.write(f"{country}: {cagr*100:.2f}%")
        
        with col3:
            st.markdown("**Volatility (CV, Last Decade)**")
            for country in compare_countries:
                if country in data.columns:
                    std_val = data.loc[year_range[1]-9:year_range[1], country].std()
                    mean_val = data.loc[year_range[1]-9:year_range[1], country].mean()
                    if mean_val > 0:
                        cv = std_val / mean_val * 100
                        st.write(f"{country}: {cv:.2f}%")
    else:
        st.warning("Please select at least 2 countries for comparison.")


# Run the application
if __name__ == "__main__":
    main()
