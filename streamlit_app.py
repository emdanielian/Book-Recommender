
##### This app is just an extremely simple example.
##### See the Streamlit documentation for how to create more complex apps.

import streamlit as st


##### Title and intro

st.title( 'Example Streamlit App' )
st.write( '''
This app is very small and does almost nothing.
It's just an example.
''' )


##### Inputs

st.header( 'Choose two numbers' )
a = st.slider( label='a', min_value=1, max_value=10, value=2, step=1 )
b = st.slider( label='b', min_value=1, max_value=10, value=3, step=1 )


##### Output

st.header( 'Tiny computations')
st.write( f'{a} + {b} = {a+b}' )
st.write( f'{a} - {b} = {a-b}' )
st.write( f'{a} * {b} = {a*b}' )
st.write( f'{a} / {b} = {a/b}' )
