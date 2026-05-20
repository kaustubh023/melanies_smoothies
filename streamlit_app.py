# Import python packages
import requests
import pandas as pd
from snowflake.snowpark.functions import col
import streamlit as st

st.title('🥤 Customize Your Smoothie! 🥤')
st.write("""Choose The Fruits You Want In Your Custom Smoothie!""")

name_on_order = st.text_input('Name On Smoothie')
st.write('The name on your Smoothie will be:', name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()

my_dataframe = session.table("smoothies.public.fruit_options").select(
    col('FRUIT_NAME'), 
    col('SEARCH_ON')
)

# Convert Snowpark dataframe to Pandas dataframe
pd_df = my_dataframe.to_pandas()

ingredients_list = st.multiselect(
    'Choose up to 5 Ingredients:',
    my_dataframe,
    max_selections=5
)

if ingredients_list:
    ingredients_string = ''
    
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        
        # Use pandas loc/iloc to get SEARCH_ON value
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen, ' is ', search_on, '.')
        
        st.subheader(fruit_chosen + ' Nutrition Information')
        smoothiefroot_response = requests.get(
            "https://my.smoothiefroot.com/api/fruit/" + search_on
        )
        sf_df = st.dataframe(
            data=smoothiefroot_response.json(), 
            use_container_width=True
        )

    my_insert_stmt = """insert into SMOOTHIES.PUBLIC.ORDERS(INGREDIENTS, NAME_ON_ORDER)
    values('""" + ingredients_string + """','""" + name_on_order + """')
    """
    
    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")
