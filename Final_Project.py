"""
Name: Matt Daley
CS230: Section 4
Data: Nuclear Explosion 1945-1998
URL: https://final-project-vb7q8kvkhfhtnytkmpzjom.streamlit.app/

Description: The interactive program provides insights into historical explosions
around the world. Explore various visualizations to understand the frequency,
location, and scale of nuclear tests and deployments by different countries.
"""

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pydeck as pdk

# read in data
def read_data():
    # converts csv to data frame in pandas
    path = "/mount/src/mattdaleyfinal/nuclear_explosions.csv"
    return pd.read_csv(path)

# [PY5] define a dictionary with the country's name and color
colors = {
    "United States": "blue",
    "Soviet Union": "red",
    "France": "cyan",
    "China": "yellow",
    "United Kingdom": "purple",
    "India": "orange",
    "Pakistan": "green",
    "Others": "grey"
    }

def welcome():
    # welcome page
    st.title("Nuclear Explosions 1945-1998")
    st.markdown("""
    Hello, my name is Matt Daley, and welcome to my Nuclear Explosion Analysis Program! 
    This interactive application provides insights into historical explosions around the world.
    Explore various visualizations to understand the frequency, location, and scale of nuclear tests and deployments by different countries.
    """)
    # [ST4] use of image
    st.image("C:/Users/daley/OneDrive - Bentley University/CS230/Final Project/nuke_photo.jpg", use_column_width=True)

    return

def annual_nuclear_explosions(df):
    st.title("Timeline of Nuclear Explosions")

    # convert date information to datetime object and create a new "Date" column
    df["Date"] = pd.to_datetime(df[["Date.Year", "Date.Month", "Date.Day"]].rename(columns={"Date.Year": "year", "Date.Month": "month", "Date.Day": "day"}))

    # [DA7] aggregate the data by year
    df["Year"] = df["Date"].dt.year
    annual_explosions = df.groupby("Year").size().reset_index(name="Counts")

    # [ST1] create slider for selected year
    min_year = annual_explosions["Year"].min()
    max_year = annual_explosions["Year"].max()
    start_year, end_year = st.slider("Select Range of Years", min_value=min_year, max_value=max_year, value=(min_year, max_year))

    # [DA5] get the count for the selected year
    selected_data = annual_explosions.loc[(annual_explosions["Year"] >= start_year) & (annual_explosions["Year"] <= end_year)]

    # [PY2]
    def get_max_and_min(selected_data):
        max_count = selected_data["Counts"].max()
        min_count = selected_data["Counts"].min()
        max_year_sentence = selected_data[selected_data["Counts"] == max_count]["Year"].iloc[0]
        min_year_sentence = selected_data[selected_data["Counts"] == min_count]["Year"].iloc[0]
        return max_count, max_year_sentence, min_count, min_year_sentence

    # sns (not taught in class)
    sns.set_style("darkgrid")
    palette = sns.color_palette("mako", as_cmap=True)

    # [VIZ1] plot line graph (sns)
    fig = plt.figure(figsize=(10, 6))
    sns.lineplot(x="Year", y="Counts", data=selected_data, marker="o", linestyle="-", color=palette(0.6))
    plt.title("Annual Nuclear Explosions", fontsize=20)
    plt.xlabel("Year", fontsize=16)
    plt.ylabel("Number of Explosions", fontsize=16)
    plt.grid(True, which="both", linestyle="--", linewidth=0.5)

    st.pyplot(fig)

    max_count, max_year_sentence, min_count, min_year_sentence = get_max_and_min(selected_data)
    # find the maximum count in the range
    st.write(f"The maximum number of nuclear explosions was {max_count} in the year {max_year_sentence}.")

    # find the minimum count in the range
    st.write(f"The minimum number of nuclear explosions was {min_count} in the year {min_year_sentence}.")

    return

def country_explosions(df, colors):
    st.title("Explosions by Country")

    # replace country abbreviations with full name
    df["WEAPON SOURCE COUNTRY"] = df["WEAPON SOURCE COUNTRY"].replace({
        "USA": "United States",
        "USSR": "Soviet Union",
        "FRANCE": "France",
        "CHINA": "China",
        "UK": "United Kingdom",
        "INDIA": "India",
        "PAKIST": "Pakistan"
    })

    # aggregate data by source country
    country_counts = df["WEAPON SOURCE COUNTRY"].value_counts()

    # determine the top four countries
    top_four_countries = country_counts.index[:4]

    # [ST2] create a multiselect for countries
    st.write("Select the countries you want to include in the pie chart: ")
    # use emojis in the multiselect options
    selected_countries = st.multiselect("Countries", country_counts.index.tolist(), default=top_four_countries.tolist())

    # filter data based on selected countries
    if selected_countries:
        filter_counts = country_counts[country_counts.index.isin(selected_countries)]
    else:
        filter_counts = pd.Series([])

    # shows the top 4 countries with all others combined if greater than 4
    if len(filter_counts) > 4:
        others = filter_counts.iloc[3:].sum()
        top_countries = filter_counts.iloc[:3]
        top_countries["Others"] = others
    else:
        top_countries = filter_counts

    # [PY4] create explode list
    explodes = [0.25 if idx == top_countries.argmax() else 0 for idx in range(len(top_countries))]

    # [PY5] determine colors for plot based on selected countries
    plot_colors = [colors.get(country, "grey") for country in top_countries.index]

    # [VIZ2] plotting using matplotlib
    if not top_countries.empty:
        fig = plt.figure(figsize=(8, 6))
        plt.pie(top_countries, autopct="%1.1f%%", startangle=90, shadow=True, explode=explodes, colors=plot_colors, pctdistance=1.2)
        plt.title("Distribution of Nuclear Explosions by Country: 1945-1998")
        plt.legend(top_countries.index, title="Countries", loc="center left", bbox_to_anchor=(1,0.5))
        st.pyplot(fig)
    else:
        st.write("No data available for selected countries.")

    return


def yield_explosions(df, top_n=10):  # [PY1]
    # [DA9]
    df["Unique Identifier"] = df["WEAPON DEPLOYMENT LOCATION"] + " (" + df["Date.Year"].astype(str) + ")"

    # group by location, then get the max yield per location
    idx = df.groupby("WEAPON DEPLOYMENT LOCATION")["Data.Yeild.Upper"].idxmax()
    top_explosions = df.loc[idx]

    # [DA3] get the top n largest explosions
    top_n_explosions = top_explosions.nlargest(top_n, "Data.Yeild.Upper")

    # create bar chart
    fig = plt.figure(figsize=(10, 6))

    # [DA2] sort the filtered dataframe by upper yield
    top_n_explosions = top_n_explosions.sort_values(by="Data.Yeild.Upper", ascending=True)

    # setting indices for bar chart
    indices = np.arange(len(top_n_explosions))
    width = 0.35

    # [VIZ3] plotting both lower and upper yield bars
    plt.barh(indices - width/2, top_n_explosions["Data.Yeild.Lower"], width, label="Lower Yield", color="lightblue")
    plt.barh(indices + width/2, top_n_explosions["Data.Yeild.Upper"], width, label="Upper Yield", color="red")

    # adding labels and title
    plt.xlabel("Yield Estimate (Kilotons of TNT)", fontsize=16)
    plt.ylabel("Location and Year of Nuclear Explosion", fontsize=16)
    plt.title(f"Top {top_n} Largest Nuclear Explosions by Yield", fontsize=20)
    plt.yticks(indices, top_n_explosions["Unique Identifier"])
    plt.legend()
    plt.tight_layout()
    st.pyplot(fig)

    # notes
    st.write("Note: No duplicate locations")
    st.write("Lower Yield: Explosion yield lower estimate in kilotons of TNT")
    st.write("Upper Yield: Explosion yield upper estimate in kilotons of TNT")

    return

def map_of_explosions(df):
    st.title("Map of Nuclear Explosions used in Combat")
    st.write("Hiroshima and Nagasaki were both bombed by the United States during World War II. "
             "This was the first and only time nuclear weapons have been used in armed conflict "
             "because of the severe consequences observed from these bombings.")

    # filter dataframe columns
    map_df = df.filter(["WEAPON DEPLOYMENT LOCATION", "Location.Cordinates.Latitude", "Location.Cordinates.Longitude"])
    map_df.columns = ["location_name", "latitude", "longitude"]

    # [DA4] filter the dataframe for Hiroshima and Nagasaki
    locations = map_df[map_df["location_name"].isin(["Hiroshima", "Nagasaki"])]

    # calculate man latitude and longitude for initial view state
    mean_latitude = locations["latitude"].mean()
    mean_longitude = locations["longitude"].mean()

    # [VIZ1] construction of map
    view_state = pdk.ViewState(latitude=mean_latitude, longitude=mean_longitude, zoom=5)
    layer1 = pdk.Layer("ScatterplotLayer", data=locations, get_position='[longitude, latitude]', get_radius=25000, get_color=[255, 0, 0, 160], pickable=True)
    layer2 = pdk.Layer("ScatterplotLayer", data=locations, get_position='[longitude, latitude]', get_radius=10000, pickable=True)
    tool_tip = {'html': 'Listing:<br> <b>{location_name}</b>', 'style': {'backgroundColor': 'lightRed', 'color': 'white'}}
    map = pdk.Deck(map_style='mapbox://styles/mapbox/dark-v9', initial_view_state=view_state, layers=[layer1, layer2], tooltip=tool_tip)
    st.pydeck_chart(map)

    return

def main():
    # convert data to pandas dataframe
    df = read_data()

    # [ST4] sidebar with radio
    option = st.sidebar.radio("Table of Contents:",
     ("Welcome", "Timeline of Explosions", "Explosions by Country", "Largest Explosions by Yield", "Map of Explosions"))
    if option == "Welcome":
        welcome()
    elif option == "Timeline of Explosions":
        annual_nuclear_explosions(df)
    elif option == "Explosions by Country":
        country_explosions(df, colors)
    elif option == "Largest Explosions by Yield":
        st.title("Largest Explosions by Yield")
        # [ST3] text box
        top_n = st.number_input("Enter the number of top nuclear explosions to display:", min_value=1, max_value=20, value=10, step=1)
        yield_explosions(df, top_n)
    elif option == "Map of Explosions":
        map_of_explosions(df)

main()
