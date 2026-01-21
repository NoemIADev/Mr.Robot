import streamlit as st
import time
import random
from game_logic import play, reset, check_winner
import pydantic 
import requests

st.set_page_config(page_title="Morpion", page_icon="⭕")
st.title("Morpion (Tic-Tac-Toe)⭕✖️")

#API_URL = "http://localhost:8000/move"  
    


##session init###
#car la session se reset a chaque clic et relis le code du debut on doit les stocké ce qui a etait fait

if "grille" not in st.session_state:
    st.session_state.grille = [""] * 9
if "player" not in st.session_state:
    st.session_state.player = "✖️"

if "winner" not in st.session_state:
    st.session_state.winner = None
if "draw" not in st.session_state:
    st.session_state.draw = False
if "running" not in st.session_state:
    st.session_state.running = False


# --- Affichage statut ---
if st.session_state.winner:
    st.success(f"🎉 Joueur {st.session_state.winner} a gagné !")
elif st.session_state.draw:
    st.warning("🤝 Match nul !")
else:
    st.info(f"À toi de jouer : {st.session_state.player}")


#button qui apelle la def reset pour recommencer
st.button("🔄 Recommencer", on_click=reset)

st.write("")

# --- Grille 3x3 ---
for row in range(3):
    cols = st.columns(3)
    for col in range(3):
        idx = row * 3 + col
        label = st.session_state.grille[idx] if st.session_state.grille[idx] else " "

        #Pour chaque case, on affiche un bouton dont le texte dépend du contenu du grille,
        # et quand on clique, on appelle play(idx) pour modifier la case correspondante."
        cols[col].button(label, key=f"cell_{idx}", on_click=play, args=(idx,))

st.write(" ")

colA, colB = st.columns(2)

with colA :
    if st.button("🎮 lancer la partie"):
         st.session_state.running = True

with colB:
     if st.button("🛑 Stop"):
        st.session_state.running = False

### faire jouer IA api

def ai_move_random(grille):
    """IA temporaire: joue au hasard sur une case vide. (à remplacer par ton API)"""
    empty = [i for i, cell in enumerate(grille) if cell == ""]
    return random.choice(empty) if empty else None

# vitesse entre chaque coup
speed = 0.5
# --- boucle "auto" : 1 coup par rerun ---
if st.session_state.running and not st.session_state.winner and not st.session_state.draw:
    idx = ai_move_random(st.session_state.grille)   # <- plus tard: appel API ici
    if idx is not None:
        play(idx)

    # petite pause pour voir l'animation
    time.sleep(speed)

    # relance pour jouer le prochain coup
    st.rerun()

# si la partie est finie, on stoppe l'auto
if st.session_state.winner or st.session_state.draw:
    st.session_state.running = False
