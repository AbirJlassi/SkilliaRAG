import json
from openai import OpenAI
import re
import os

if "OPENAI_API_KEY" not in os.environ:
        raise EnvironmentError("OPENAI_API_KEY non défini dans les variables d'environnement")
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

def load_taxonomy(taxonomy_path="config/taxonomie.json"):
    """Charge la taxonomie depuis un fichier JSON."""
    with open(taxonomy_path, "r", encoding="utf-8") as f:
        return json.load(f)

def annotate_with_llm(text, taxonomy, model="gpt-3.5-turbo"):
    """
    Utilise un LLM pour annoter un texte selon la taxonomie fournie.
    Retourne un dict {catégorie: sous-catégorie}.
    """
    taxonomy_str = json.dumps(taxonomy, ensure_ascii=False, indent=2)

    prompt = f"""
Tu es un assistant qui lit un texte et l'annote en fonction de la taxonomie ci-dessous.
Pour chaque catégorie, choisis au maximum UNE sous-catégorie qui correspond au texte.

Taxonomie :
{taxonomy_str}

Règles :
- Retourne UNIQUEMENT un JSON valide, sans texte avant ou après.
- Format attendu : {{"Catégorie": "Sous-catégorie", ...}}
- Si aucune correspondance, ne mets pas la catégorie.
- Tu peux inférer le sens même si les mots exacts ne sont pas présents.

Texte à analyser :
\"\"\"
{text}
\"\"\"

Réponds uniquement ainsi :
<json>
{{ ... }}
</json>
"""

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    raw_output = response.choices[0].message.content.strip()

    # Extraction du JSON entre <json> ... </json>
    match = re.search(r"<json>(.*?)</json>", raw_output, re.DOTALL)
    if match:
        json_str = match.group(1).strip()
    else:
        json_str = raw_output  # fallback si pas de balises

    # Tentative de parsing
    try:
        tags = json.loads(json_str)
    except json.JSONDecodeError:
        tags = {}

    return tags


taxonomy_path = "config/taxonomie.json"

def enrich_taxonomy(new_tags, taxonomy_file=taxonomy_path):
    """Ajoute les nouvelles annotations dans le fichier de taxonomie."""
    # Charger la taxonomie existante
    with open(taxonomy_file, "r", encoding="utf-8") as f:
        taxonomy = json.load(f)

    # Parcourir les nouveaux tags détectés
    for category, sub_value in new_tags.items():
        if isinstance(sub_value, dict):  
            # Cas LLM: {"Secteurs d'activité": {"Services Financiers": ["banque commerciale"]}}
            for subcat, keywords in sub_value.items():
                if subcat not in taxonomy.get(category, {}):
                    taxonomy[category][subcat] = []
                for kw in keywords:
                    if kw not in taxonomy[category][subcat]:
                        taxonomy[category][subcat].append(kw)
        else:
            # Cas regex: {"Secteurs d'activité": "Services Financiers"}
            subcat = sub_value
            if subcat not in taxonomy.get(category, {}):
                taxonomy[category][subcat] = []

    # Sauvegarder la taxonomie enrichie
    with open(taxonomy_file, "w", encoding="utf-8") as f:
        json.dump(taxonomy, f, indent=2, ensure_ascii=False)

    return taxonomy




# --- Exemple ---
if __name__ == "__main__":
    taxonomy = load_taxonomy("config/taxonomie.json")
    sample_text = """
    Ce projet de migration cloud pour une banque commerciale inclut
    l'implémentation d'une infrastructure réseau sécurisée dans un datacenter.
    """
    tags = annotate_with_llm(sample_text, taxonomy)
    print("Tags détectés :", tags)