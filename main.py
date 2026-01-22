from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx

app = FastAPI(title="TicTacToe LLM API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_MORPION_URL_1 = "http://localhost:8001/coup_morpion_openai"
API_MORPION_URL_2 = "http://localhost:8002/coup_morpion"

WIN_COMBOS = [
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
]

PROMPT_TEST = """ You are playing Tic-Tac-Toe. STRICT RULES (MANDATORY): 
- You MUST respond with ONLY ONE CHARACTER 
- This character MUST be a digit between 0 and 8 
- The number MUST correspond to an EMPTY cell 
- DO NOT explain 
- DO NOT add text 
- DO NOT add punctuation 
- DO NOT add JSON 
- DO NOT add new lines 
- DO NOT add anything if cell not "" 
an empty cell is always represented by "" 
add something only if the cell is not occupied STRATEGY GOAL: 
- Always play the move that increases your chances to WIN 
- Block the opponent from winning if necessary 
- Prefer a winning move if available 
- Otherwise, make the best strategic move possible If you break any rule, the response is INVALID. POSITION MAPPING (this never changes): 
┌───┬───┬───┐ 
│ 0 │ 1 │ 2 │ 
├───┼───┼───┤ 
│ 3 │ 4 │ 5 │ 
├───┼───┼───┤ 
│ 6 │ 7 │ 8 │ 
└───┴───┴───┘ 
Board (index 0 to 8): {grille} Current player: {joueur} 
Your choice = One number only ! """

class JeuMorpion(BaseModel):
    grille: list[str]
    joueur: str


def joueur_suivant(joueur: str):
    return "o" if joueur == "x" else "x"


def victoire(grille: list[str], joueur: str) -> bool:
    return any(all(grille[i] == joueur for i in combo) for combo in WIN_COMBOS)


class JeuMorpionComplet(BaseModel):
    PROMPT: str
    grille: list[str]
    joueur: str
    model_name: str = "llama3:latest"


async def jouer_coup_ia(
    client: httpx.AsyncClient, jeu: JeuMorpion, api_url: str
) -> int:
    
    response = await client.post(api_url, json=jeu.model_dump())

    if response.status_code != 200:
        raise HTTPException(response.status_code, response.text)

    data = response.json()

    if "index" not in data:
        raise HTTPException(500, "Réponse IA invalide")

    coup = int(data["index"])

    if coup < 0 or coup > 8 or jeu.grille[coup] != "":
        raise HTTPException(500, "Coup non autorisé")
    return coup


# chemin auto
@app.post("/joue_auto")
async def jouer_auto():
    
    jeu = JeuMorpionComplet(
        PROMPT=PROMPT_TEST,
        grille=["", "", "", "", "", "", "", "", ""],
        joueur="o"
    )

    async with httpx.AsyncClient(timeout=10) as client:
        while "" in jeu.grille:
            api_url = API_MORPION_URL_1 if jeu.joueur == "x" else API_MORPION_URL_2

            coup = await jouer_coup_ia(client, jeu, api_url)
            jeu.grille[coup] = jeu.joueur

            if victoire(jeu.grille, jeu.joueur):
                return {"vainqueur": jeu.joueur, "grille": jeu.grille}

            jeu.joueur = joueur_suivant(jeu.joueur)

    return {"vainqueur": None, "grille": jeu.grille}
