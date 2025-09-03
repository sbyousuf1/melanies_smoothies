# Import python packages
import streamlit as st
cnx = st.connection("snowflake")
from snowflake.snowpark.functions import col

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
            
# New section to display smoothiefroot nutrition information
import requests
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
st.text(smoothiefroot_response.json())

