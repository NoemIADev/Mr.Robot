from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from ollama import chat

app = FastAPI()

class JeuMorpion(BaseModel):
    PROMPT: str
    grille: list[str]
    joueur: str
    model_name: str = "llama3:latest"


@app.post("/coup_morpion")
def jouer_coup(jeu: JeuMorpion):
    MAX_TENTATIVES = 5
    coups_essayes = [] 

    for tentative in range(1, MAX_TENTATIVES + 1):
        print(f"\nTentative {tentative}/{MAX_TENTATIVES}")

        positions_vides = [i for i, c in enumerate(jeu.grille) if c == ""]

        if tentative == 1:
            prompt_a_utiliser = jeu.PROMPT
        else:
            prompt_a_utiliser = (
                jeu.PROMPT
                + f"""

ATTENTION - YOUR PREVIOUS ATTEMPTS FAILED:
- You already tried: {coups_essayes} (INVALID!)
- EMPTY positions available: {positions_vides}
- You MUST choose from: {positions_vides}
- DO NOT choose from: {coups_essayes}

Choose wisely this time!
"""
            )

        response = chat(
            model=jeu.model_name,
            messages=[
                {
                    "role": "user",
                    "content": prompt_a_utiliser.format(
                        grille=jeu.grille, joueur=jeu.joueur
                    ),
                }
            ],
        )

        try:
            index = int(response.message.content.strip())
            print(f"IA choisit: {index}")
        except ValueError:
            print(f"Réponse invalide: '{response.message.content}'")
            continue

        # Ajouter à la liste des tentatives
        coups_essayes.append(index)

        # Valider
        if index < 0 or index > 8:
            print(f"Hors limites: {index}")
            continue

        if jeu.grille[index] != "":
            print(f"Case {index} occupée")
            continue

        # Si tout est bon
        print(f"Coup valide: {index}")

        nouvelle_grille = jeu.grille.copy()
        nouvelle_grille[index] = jeu.joueur

        return {
            "index": index,
            "joueur": jeu.joueur,
            "grille": nouvelle_grille,
            "tentatives": tentative,
            "coups_essayes": coups_essayes,
        }

    print(f"Échec après {MAX_TENTATIVES} tentatives")
    positions_vides = [i for i, c in enumerate(jeu.grille) if c == ""]

    if positions_vides:
        index = positions_vides[0]
        nouvelle_grille = jeu.grille.copy()
        nouvelle_grille[index] = jeu.joueur

        return {
            "index": index,
            "joueur": jeu.joueur,
            "grille": nouvelle_grille,
            "fallback": True,
        }

    raise HTTPException(500, "Aucune position disponible")
