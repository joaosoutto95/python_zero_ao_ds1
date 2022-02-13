# imports:
import pandas as pd
from IPython.core.display import HTML
import seaborn as sns
import plotly.express as px
import matplotlib.pyplot as plt
from matplotlib import gridspec
import ipywidgets as widgets
from ipywidgets import fixed
import streamlit as st #TO RUN STREAMLIT  =====>     !streamlit hello
#-----------------------------------------------------------------------------------------------

# Initial text output:
st.title('Real Estate Business Analysis')
st.markdown('Welcome! This is the visualization tool developed to understand the business opportunities in the area '
            'of Seattle city')
st.header('Filtered Data:')
st.sidebar.header('Filters:')

# Defined functions:
@st.cache(allow_output_mutation= True)
    # Function to read data:
def get_data(path):
    data = pd.read_csv(path)
    return data

    # Function to load data in an interactive map:
def interactive_map(df_map):
    map_interactive = px.scatter_mapbox(
        df_map,
        lat='lat',
        lon='long',
        color='price',
        size='price',
        color_continuous_scale=px.colors.sequential.Rainbow,
        size_max=15,
        zoom=10
    )
    map_interactive.update_layout(mapbox_style='open-street-map')
    map_interactive.update_layout(height=600, margin={'r': 0, 't': 0, 'l': 0, 'b': 0})
    return st.plotly_chart(map_interactive)

#-----------------------------------------------------------------------------------------------

# Loading data:
path = 'C:/Users/jps/Desktop/Python/repos/python_zero_ao_ds1/datasets/house_rocket/kc_house_data.csv'
df = get_data(path)

#-----------------------------------------------------------------------------------------------
# Drop useless columns:
df = df.drop(columns =['sqft_living15','sqft_lot15'])

# Date to datetime64 in YYYY-MM-DD format:
df['date'] = df['date'].str.slice(stop=8)
df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')

# Converting sqft to m² in all columns except sqft_living because that will be done after classification with benchmark:
df[['sqft_lot','sqft_above','sqft_basement']].apply(lambda x: x*0.092903)

# Classification of N° BEDROOMS, PRICE, WATERFRONT and SQFT_LIVING through benchmark:
    # Dormitory types definition:
df['dormitory_type'] = df['bedrooms'].apply(lambda x: 'studio' if (x == 0)|(x == 1) else ('apartment' if x == 2 else 'house'))

    # Standard definition:
df['standard'] = pd.cut(df['price'], [0, 540000, 10000000], labels = ['High','Low'])

    # Water front definition:
df['is_waterfront'] = df['waterfront'].apply(lambda x: 'yes' if (x == 1) else 'no')

    # Size type definition:
df['size_type'] = pd.cut(df['sqft_living'], [0,1427,1910,2550,50000], labels = ['Size 0','Size 1','Size 2','Size 3'])

# Creating a year, week and day column:
df['date_yr'] = df['date'].dt.year
df['date_ywk'] = df['date'].dt.strftime( '%Y-Week-%U' )
df['date_day'] = df['date'].dt.strftime( '%d-%m-%Y' )

#-----------------------------------------------------------------------------------------------

# Filters:
    # Num. of bedrooms:
bedrooms = st.sidebar.multiselect(
    'N° of bedrooms:',
    pd.unique(df['bedrooms'].sort_values(ascending=True))
)

     # Price range:
x_min = int(df['price'].min())
x_mean = int(df['price'].mean())
x_max = int(df['price'].max())
price_slider = st.sidebar.slider(
    'Price Range:',
    x_min,
    x_max,
    x_mean
)

    # Filter by properties with water view:
house_waterfront = st.sidebar.selectbox('Property with waterfront:',
                                        pd.unique(df['is_waterfront']))

    # Display map or not:
is_check = st.sidebar.checkbox('Display Map')
#-----------------------------------------------------------------------------------------------

# Loading to streamlit:

    # Conditionals for data filtering:
df_filtered = df
if bedrooms:
    df_filtered = df[(df['bedrooms'].isin(bedrooms)) &
                     (df['price'] <= price_slider) &
                     (df['is_waterfront']== house_waterfront)]
else:
    df_filtered = df[(df['price'] <= price_slider) &
                     (df['is_waterfront'] == house_waterfront)]
    # Filtered Dataframe with shape:
st.dataframe(df_filtered)
st.write('Properties found in filtered data:', df_filtered.shape[0])

    # Filtered Map:
st.header('Map Visualization:')
if is_check:
    interactive_map(df_filtered)

