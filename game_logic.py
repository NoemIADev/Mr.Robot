### def des fonction de jeu
import streamlit as st
import requests

API_URL = "http://localhost:8000/move"

#devinir les gagnant 
def check_winner(b):
    wins = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8),  # lignes
        (0, 3, 6), (1, 4, 7), (2, 5, 8),  # colonnes
        (0, 4, 8), (2, 4, 6)              # diagonales
    ]
    for i, j, k in wins:
        if b[i] and b[i] == b[j] == b[k]:
            return b[i]
    return None

def play(idx):
    # si partie finie ou case déjà prise -> rien
    if st.session_state.winner or st.session_state.draw:
        return
    if st.session_state.grille[idx] != "":
        return

    # jouer le coup
    st.session_state.grille[idx] = st.session_state.player

    # vérifier gagnant
    w = check_winner(st.session_state.grille)
    if w:
        st.session_state.winner = w
        return

    # vérifier match nul
    if all(cell != "" for cell in st.session_state.grille):
        st.session_state.draw = True
        return

    # changer de joueur
    st.session_state.player = "⭕" if st.session_state.player == "✖️" else "✖️"

#pour remmetre la partie a zero
def reset():
    st.session_state.grille = [""] * 9
    st.session_state.player = "✖️"
    st.session_state.winner = None
    st.session_state.draw = False

#apel api
def call_ai_api(grille, player):
    payload = {
        "grille": grille,     # état actuel du jeu
        "player": player   # "X" ou "O" (qui doit jouer maintenant)
    }

    response = requests.post(API_URL, json=payload, timeout=10)
    response.raise_for_status() #= si sa marche pas arrete toi la

    data = response.json()

    # si l'API renvoie directement la liste
   # if isinstance(data, list):
       # return data

    # si l'API renvoie un JSON
    return data["grille"]