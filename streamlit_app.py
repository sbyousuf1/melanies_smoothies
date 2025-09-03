# Import python packages
import streamlit as st
cnx = st.connection("snowflake")
from snowflake.snowpark.functions import col
import requests
import pandas as pd

session = cnx.session()

# Write directly to the app
st.title(":cup_with_straw: Customize your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input("Name on Smoothie:", key="name_input")
st.write("The name on your Smoothie will be:", name_on_order)

fruit_df = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
fruit_list = [row['FRUIT_NAME'] for row in fruit_df.collect()]

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_list,
    max_selections=5,
    key="ingredients_select"
)

# Add nutrition information section
if ingredients_list:
    st.subheader("Nutrition Information")
    
    # Calculate total nutrition values
    total_nutrition = {
        "carbs": 0,
        "fat": 0,
        "protein": 0,
        "sugar": 0
    }
    
    # Create columns for displaying fruits
    cols = st.columns(len(ingredients_list))
    
    # Fetch and display nutrition info for each selected fruit
    for idx, fruit in enumerate(ingredients_list):
        with cols[idx]:
            st.markdown(f"**{fruit}**")
            try:
                response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{fruit.lower()}")
                if response.status_code == 200:
                    nutrition_data = response.json()
                    
                    # Display individual fruit nutrition
                    st.markdown(f"🍎 Carbs: {nutrition_data['carbs']}g")
                    st.markdown(f"🥑 Fat: {nutrition_data['fat']}g")
                    st.markdown(f"🥩 Protein: {nutrition_data['protein']}g")
                    st.markdown(f"🍯 Sugar: {nutrition_data['sugar']}g")
                    
                    # Add to totals
                    for key in total_nutrition:
                        total_nutrition[key] += nutrition_data[key]
                else:
                    st.warning(f"Could not fetch nutrition data for {fruit}")
            except Exception as e:
                st.error(f"Error fetching nutrition data for {fruit}")
    
    # Display total nutrition
    st.markdown("---")
    st.subheader("Total Nutrition Values")
    total_cols = st.columns(4)
    with total_cols[0]:
        st.metric("Total Carbs", f"{total_nutrition['carbs']:.1f}g")
    with total_cols[1]:
        st.metric("Total Fat", f"{total_nutrition['fat']:.1f}g")
    with total_cols[2]:
        st.metric("Total Protein", f"{total_nutrition['protein']:.1f}g")
    with total_cols[3]:
        st.metric("Total Sugar", f"{total_nutrition['sugar']:.1f}g")

    ingredients_string = ', '.join(ingredients_list)
    
    time_to_insert = st.button('Submit Order', key="submit_button")
    
    if time_to_insert:
        try:
            insert_query = f"""
            INSERT INTO smoothies.public.orders (ingredients, name_on_order)
            SELECT '{ingredients_string}', '{name_on_order.replace("'", "''")}'
            """
            
            session.sql(insert_query).collect()
            st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")
        except Exception as e:
            st.error(f"Error placing order: {str(e)}")
