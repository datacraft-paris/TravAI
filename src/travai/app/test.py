import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import random


# Générer des données aléatoires pour deux séries
data = pd.DataFrame({
    'valeurs_1': np.random.randn(500),
    'valeurs_2': np.random.randn(500)
})

# Transformer les données en format long pour distinguer les deux séries
data_long = data.melt(var_name='groupe', value_name='valeur')

# Créer un histogramme superposé avec Altair
chart = alt.Chart(data_long).mark_bar(opacity=0.5).encode(
    alt.X("valeur:Q", bin=alt.Bin(maxbins=30), title="Valeurs"),
    alt.Y("count()", title="Fréquence"),
    alt.Color("groupe:N", title="Groupe")
).properties(
    title="Histogramme Superposé"
)

# Ajouter une case à cocher pour afficher une ligne horizontale
if st.checkbox("Afficher la ligne horizontale"):
    # Par exemple, on place la ligne horizontale à y=10
    line = alt.Chart(pd.DataFrame({'y': [10]})).mark_rule(
        strokeDash=[5, 5],
        color='red'
    ).encode(
        y=alt.Y('y:Q')
    )
    # Superposer la ligne à l'histogramme
    chart = chart + line

# Afficher l'histogramme dans Streamlit
st.altair_chart(chart, use_container_width=True)


# Générer trois nombres aléatoires entre 1 et 100
chiffre1 = random.randint(1, 100)
chiffre2 = random.randint(1, 100)
chiffre3 = random.randint(1, 100)

# Générer des valeurs de delta aléatoires (entre -10 et 10)
delta1 = random.randint(-10, 10)
delta2 = random.randint(-10, 10)
delta3 = random.randint(-10, 10)

# Organiser l'affichage des metrics côte à côte grâce à des colonnes
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Chiffre 1", value=chiffre1, delta=delta1)
with col2:
    st.metric(label="Chiffre 2", value=chiffre2, delta=delta2)
with col3:
    st.metric(label="Chiffre 3", value=chiffre3, delta=delta3)