import streamlit as st


st.set_page_config(page_title="Morpion", page_icon="⭕")
st.title("Morpion (Tic-Tac-Toe)⭕✖️")

##session init###
#car la session se reset a chaque clic et relis le code du debut on doit les stocké ce qui a etait fait

if "board" not in st.session_state:
    st.session_state.board = [""] * 9
if "player" not in st.session_state:
    st.session_state.player = "✖️"

if "winner" not in st.session_state:
    st.session_state.winner = None
if "draw" not in st.session_state:
    st.session_state.draw = False

###definir le gagnant###

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
    if st.session_state.board[idx] != "":
        return

    # jouer le coup
    st.session_state.board[idx] = st.session_state.player

    # vérifier gagnant
    w = check_winner(st.session_state.board)
    if w:
        st.session_state.winner = w
        return

    # vérifier match nul
    if all(cell != "" for cell in st.session_state.board):
        st.session_state.draw = True
        return

    # changer de joueur
    st.session_state.player = "⭕" if st.session_state.player == "✖️" else "✖️"

#pour remmetre la partie a zero
def reset():
    st.session_state.board = [""] * 9
    st.session_state.player = "✖️"
    st.session_state.winner = None
    st.session_state.draw = False


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
        label = st.session_state.board[idx] if st.session_state.board[idx] else " "

        #Pour chaque case, on affiche un bouton dont le texte dépend du contenu du board,
        # et quand on clique, on appelle play(idx) pour modifier la case correspondante.”
        cols[col].button(label, key=f"cell_{idx}", on_click=play, args=(idx,))

st.write(" ")

st.button("🎮 lancer la partie", on_click="")


