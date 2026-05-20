# Import python packages
import requests 
from snowflake.snowpark.functions import col
import streamlit as st
# from snowflake.snowpark.context import get_active_session

st.title('🥤 Customize Your Smoothie! 🥤')
st.write("""Choose The Fruits You Want In Your Custom Smoothie!""")

name_on_order = st.text_input('Name On Smoothie')
st.write('The name on your Smoothie will be:', name_on_order)

cnx=st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

# ✅ Added max_selections=5
ingredients_list = st.multiselect(
    'Choose up to 5 Ingredients:',
    my_dataframe,
    max_selections=5
)

if ingredients_list:
    ingredients_string = ''
    
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        st.subheader(fruit_chosen + 'Nutrition Information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon"+ fruit_chosen)
        sf_df =st.dataframe(data=smoothiefroot_response.json(),use_container_width=True)
        
    my_insert_stmt = """insert into SMOOTHIES.PUBLIC.ORDERS(INGREDIENTS, NAME_ON_ORDER)
    values('""" + ingredients_string + """','""" + name_on_order + """')
    """

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")


 


