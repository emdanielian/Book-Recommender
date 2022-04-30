import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
data = pd.read_csv('practice-project-dataset-1.csv')

st.title('Mortgage Data by Race and Sex')
st.subheader('A tool used to plot fraction of approved mortgage applications against median property value for each state, sorted by race and sex.')

sex_list = []
for sex in data['derived_sex']:
    if sex not in sex_list:
        sex_list.append(sex)

race_list = []
for race in data['derived_race']:
    if race not in race_list:
        race_list.append(race)

selected_sex = st.selectbox("Select a sex from the dropdown:", sex_list)
selected_race = st.selectbox("Select a race from the dropdown:", race_list)
st.write()

filtered_data = data[(data['derived_race']==selected_race) & (data['derived_sex']==selected_sex)].copy()

filtered_data['approved'] = np.where(filtered_data['action_taken'] < 3, 1, 0)
filtered_data.head()

filtered_data['property_value'] = filtered_data['property_value'].replace('Exempt', np.nan).astype(float)

final = filtered_data.groupby('state_code')[['property_value', 'approved']].agg( {'property_value' : 'median', 'approved': 'mean' } )

fig = plt.figure()
plt.scatter(final['property_value'], final['approved'], c='royalblue')
plt.xlabel('Median Property Value')
plt.ylabel('Fraction of Applications Approved')
plt.title('Fraction of Applications vs Median Property Value by State')
st.write(fig)