import streamlit as st
import pandas as pd
import pydeck as pdk
from datetime import datetime


# import data
listing = pd.read_csv("listing_pro.csv", parse_dates=["host_since"])

# column setup
col1, col2 = st.columns(2)

# ***** Section 1 *****
# Filtering
with col1:
    # filterings
    # 1. price range slider
    price_min, price_max = int(listing['price'].min()), int(listing['price'].max())
    selected_price = st.slider('Please select your price budget: ', price_min, price_max, (price_min, price_max))
    # 2. host since slider
    host_since = pd.to_datetime(listing['host_since'])
    host_since_time = st.slider("Host since",value=datetime(host_since.min().year,host_since.min().month,host_since.min().day),format="MM-DD-YY",)
    st.write("Host since:", host_since_time)
    # 3. Availability
    agree = st.checkbox("Available for booking")
    if agree:
        avail = "f"
    else:
        avail = "s"
    # 4. Min nights & Max nights
    min_nights = st.number_input("Please input the minimum nights:",step=1,value=listing['minimum_nights'].min())
    max_nights = st.number_input("Please input the maximum nights:",step=1,value=listing['minimum_nights'].max())
    st.write("Minimum stays for ", min_nights, " & Maximum stays for ",max_nights)

filtered_data = listing[
    (listing['price'] >= selected_price[0]) &
    (listing['price'] <= selected_price[1]) &
    (listing['host_since'] > pd.to_datetime(host_since_time)) &
    (listing['has_availability'] != avail) &
    (listing['minimum_nights'] >= min_nights) &
    (listing['minimum_nights'] <= max_nights)
    ]

st.write("Current Filtered items:", len(filtered_data))

# map visuals
with col2:
    map_style = 'mapbox://styles/mapbox/streets-v11'
    # pydeck
    st.pydeck_chart(pdk.Deck(
        map_style=map_style,
        initial_view_state=pdk.ViewState(
            latitude=listing['latitude'].mean(),
            longitude=listing['longitude'].mean(),
            zoom=11,
            pitch=50,
        ),
        layers=[
            pdk.Layer(
                'ScatterplotLayer',
                data=filtered_data,
                get_position='[longitude, latitude]',

                get_radius=60,
                pickable=True,
            ),
        ],
        tooltip={"html": "<b>Price:</b> ${price} <br/><b>Host name:</b> {host_name}", "style": {"color": "white"}}
    ))


# ***** Section 1 *****
# host name
with col1:
    host_name = st.text_input("Please input Host Name:")
    host_data = listing[listing['host_name'] == host_name]
    if st.button("Search"):
        host_data = listing[listing['host_name'] == host_name]
        if host_data.empty:
            st.write("No result for the host name. Please check the name.")
        else:
            col3, col4 = st.columns(2)
            # 在第一列绘制房价散点图
            with col3:
                st.write(f"{host_name} - Price Distribution")
                scatter_data = host_data.reset_index(drop=True)[['price']]
                # scatter_data['index'] = scatter_data.index  # 添加一个索引列作为X轴
                st.scatter_chart(scatter_data.rename(columns={'price': 'Price ($)'}))

            # 在第二列绘制评分直方图
            with col4:
                st.write(f"{host_name} - Reviews Score")
                score_counts = host_data['review_scores_rating'].value_counts(bins=8).sort_index()
                score_counts.index = score_counts.index.astype(str)
                st.bar_chart(score_counts)

# show result
with col2:
    st.map(host_data, color = "#0044ff", size = 30)