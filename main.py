from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("API_KEYS")
if not API_KEY:
    raise RuntimeError("API_KEYS manquant dans le .env")

ENDPOINT = "https://llm-res-ttt.cognitiveservices.azure.com/openai/v1/"
DEPLOYMENT_NAME = "gpt-4o"

client = OpenAI(
    base_url=ENDPOINT,
    api_key=API_KEY,
)

app = FastAPI()


class JeuMorpion(BaseModel):
    PROMPT: str
    grille: list[str]
    joueur: str
    model_name: str = DEPLOYMENT_NAME


@app.post("/coup_morpion_openai")
def jouer_coup_openai(jeu: JeuMorpion):
    jeu.model_name = DEPLOYMENT_NAME
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

Return ONLY the index (number).
"""
            )

        response = client.chat.completions.create(
            model=jeu.model_name,
            messages=[
                {
                    "role": "user",
                    "content": prompt_a_utiliser.format(
                        grille=jeu.grille,
                        joueur=jeu.joueur,
                    ),
                }
            ],
            temperature=0,
        )

        content = response.choices[0].message.content.strip()

        try:
            index = int(content)
        except ValueError:
            continue

        coups_essayes.append(index)

        if index < 0 or index > 8:
            continue

        if jeu.grille[index] != "":
            continue

        nouvelle_grille = jeu.grille.copy()
        nouvelle_grille[index] = jeu.joueur

        return {
            "index": index,
            "joueur": jeu.joueur,
            "grille": nouvelle_grille,
            "tentatives": tentative,
            "coups_essayes": coups_essayes,
        }

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
