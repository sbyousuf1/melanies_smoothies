# Import python packages
import streamlit as st
cnx = st.connection("snowflake")
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(":cup_with_straw: Customize your Smoothie! :cup_with_straw:")
st.write(
  """Choose the fruits you want in your custom Smoothie!"""
)

session = cnx.session()

# Write directly to the app (removed duplicates)
st.title(":cup_with_straw: Customize your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Added unique key to text_input
name_on_order = st.text_input("Name on Smoothie:", key="name_input")
st.write("The name on your Smoothie will be:", name_on_order)

fruit_df = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
fruit_list = [row['FRUIT_NAME'] for row in fruit_df.collect()]

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_list,
    max_selections=5,
    key="ingredients_select"  # Added unique key
)

if ingredients_list:
    ingredients_string = ', '.join(ingredients_list)
    
    time_to_insert = st.button('Submit Order', key="submit_button")  # Added unique key
    
    if time_to_insert:
        insert_stmt = """
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES (?, ?)
        """
        
        try:
            session.sql(insert_stmt).bind_params(ingredients_string, name_on_order).collect()
            st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")
        except Exception as e:
            st.error(f"Error placing order: {str(e)}")
