# type: ignore
# flake8: noqa
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#| label: load-tract-data
import pandas as pd
ipums_df = pd.read_csv("assets/nhgis0001_ds254_20215_tract.csv", encoding_errors='ignore')
ipums_df.head()
#
#
#
#
#
#| label: install-itables
# Here you can uncomment the following to install itables,
# if it is not already installed in your environment!
# We just use this to display nice HTML tables with pagination,
# so it's optional and you don't need to worry if it
# fails to install for whatever reason.
#!pip install itables
#
#
#
#| label: tract-counts
from itables import show
tract_counts = ipums_df['STUSAB'].value_counts().to_frame().reset_index()
show(tract_counts)
#
#
#
#
#
#| label: select-dmv-states
states_to_include = [
    'District of Columbia',
    'Maryland',
    'Virginia'
]
dmv_df = ipums_df[ipums_df['STATE'].isin(states_to_include)].copy()
#
#
#
#
#
#| label: county-counts
county_counts = dmv_df['COUNTY'].value_counts(dropna=False)
show(county_counts)
#
#
#
#
#
#| label: select-counties
counties = [
    'Fairfax County', # 274 tracts
    'Montgomery County', # 255 tracts
    "Prince George's County", # 214 tracts
    'District of Columbia', # 206 tracts
    'Arlington County', # 71 tracts
    'Alexandria city', # 48 tracts
    'Fairfax city', # 5 tracts
    'Falls Church city', # 3 tracts
]
dmv_df = dmv_df[dmv_df['COUNTY'].isin(counties)].copy()
#
#
#
#
#
#| label: geo-id-to-string
# String version for merging
dmv_df['TL_GEO_ID_str'] = dmv_df['TL_GEO_ID'].apply(str)
#
#
#
#
#
#
#
#
#
#| label: install-geopandas
# Uncomment the following to install geopandas, if it is
# not already installed in your environment!
#!pip install geopandas
#
#
#
#| label: load-shapefiles
import geopandas as gpd
# Shapefiles
dc_shape_df = gpd.read_file("assets/tl_2021_11_tract/tl_2021_11_tract.shp")
md_shape_df = gpd.read_file("assets/tl_2021_24_tract/tl_2021_24_tract.shp")
va_shape_df = gpd.read_file("assets/tl_2021_51_tract/tl_2021_51_tract.shp")
dmv_shape_df = pd.concat([dc_shape_df,md_shape_df,va_shape_df], ignore_index=True)
#
#
#
#
#
#| label: merge-data-with-shapes
geo_df_pd = pd.merge(dmv_df, dmv_shape_df, left_on='TL_GEO_ID_str', right_on='GEOID', how='left')
geo_df = gpd.GeoDataFrame(geo_df_pd)
geo_df.set_index('GEOID', inplace=True)
#
#
#
#
#
#| label: install-plotly
# Uncomment the following to install Plotly, if it is not already
# installed on your machine!
#!pip install plotly
#
#
#
#| label: cloropeth-map
from plotly import graph_objs as go
median_income_var = "AOQIE001"
# Capitol Building
#capitol_lat = 38.889805
#capitol_lon = -77.009056
# White House
#center_lat = 38.8977
#center_lon = -77.0365
# Scott Statue
center_lat = 38.907278946266466
center_lon = -77.03651807332851

fig = go.Figure(
    go.Choroplethmapbox(
        geojson=geo_df.__geo_interface__,
        locations=geo_df.index,
        z=geo_df[median_income_var],
        autocolorscale=True,
        marker_opacity=0.7,
        marker_line_width=1,
        hoverinfo='location+z+text+name'
    )
)
fig.update_layout(
    #autosize=False,
    width=800,
    height=800,
    mapbox_style="open-street-map",
    mapbox_zoom=10.4,
    mapbox_center = {
        "lat": center_lat,
        "lon": center_lon
    }
)
#fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.show()
#
#
#
#
#
#
#
#
#| label: cloropeth-map-categories
import plotly.express as px
from plotly import graph_objs as go
median_income_var = "AOQIE001"
# Capitol Building
#capitol_lat = 38.889805
#capitol_lon = -77.009056
# White House
center_lat = 38.8977
center_lon = -77.0365

# Here we'll drop NA, since Plotly doesn't handle
# NA values as well as NaN values
geo_df_nona = geo_df[~pd.isna(geo_df[median_income_var])].copy()
# Cutpoints
#natl_median = 70000
metro_median = 110355
low_cutoff = (2/3) * natl_median
high_cutoff = 2 * natl_median
def get_income_level(income):
    # If NA, we want to keep its category as NA
    if pd.isna(income):
        return pd.NA
    if income < low_cutoff:
        return "Low"
    if income > high_cutoff:
        return "High"
    return "Medium"
geo_df_nona['income_level'] = geo_df_nona[median_income_var].apply(get_income_level)
print(geo_df_nona['income_level'].head())

fig = px.choropleth_mapbox(geo_df_nona,
  geojson=geo_df_nona.geometry,
  color="income_level",
  locations=geo_df_nona.index,
  #featureidkey="properties.district",
  center={"lat": center_lat, "lon": center_lon},
  mapbox_style="carto-positron",
  zoom=10,
  color_discrete_map={
    'High': 'green',
    'Medium': 'lightgrey',
    'Low': 'red'
  }
)
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.show()
#
#
#
