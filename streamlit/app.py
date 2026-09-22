import streamlit as st

st.title("🚀 Test de l'application MLOps")
st.write("Si vous voyez ce message, votre application Streamlit fonctionne parfaitement !")

# Petit test interactif basique
nom = st.text_input("Comment vous appelez-vous ?")
if nom:
    st.success(lettres := f"Bienvenue à bord, {nom} !")

    # Test d'un graphique simple
    import pandas as pd
    import numpy as np

    chart_data = pd.DataFrame(
        np.random.randn(20, 3),
        columns=['a', 'b', 'c']
    )
    st.line_chart(chart_data)
