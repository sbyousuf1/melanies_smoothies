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

if ingredients_list:
    st.subheader("Nutrition Information")
    
    # Create tabs for each selected fruit
    tabs = st.tabs(ingredients_list)
    
    # Fetch and display nutrition info for each selected fruit
    for idx, fruit in enumerate(ingredients_list):
        with tabs[idx]:
            try:
                # Make API call for each fruit
                response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{fruit.lower()}")
                if response.status_code == 200:
                    # Convert JSON response to DataFrame and display
                    nutrition_data = response.json()
                    nutrition_df = pd.DataFrame([nutrition_data])
                    st.dataframe(nutrition_df, use_container_width=True)
                else:
                    st.warning(f"Could not fetch nutrition data for {fruit}")
            except Exception as e:
                st.error(f"Error fetching nutrition data for {fruit}: {str(e)}")

    ingredients_string = ', '.join(ingredients_list)
    
    time_to_insert = st.button('Submit Order', key="submit_button")

    if time_to_insert:
        try:
            # Using SQL parameters with proper escaping
            insert_query = f"""
            INSERT INTO smoothies.public.orders (ingredients, name_on_order)
            SELECT '{ingredients_string}', '{name_on_order.replace("'", "''")}'
            """
            
            session.sql(insert_query).collect()
            st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")
        except Exception as e:
            st.error(f"Error placing order: {str(e)}")
