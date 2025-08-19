import json
import re

def load_taxonomy(taxonomy_path="config/taxonomie.json"):
    """Charge la taxonomie depuis un fichier JSON."""
    with open(taxonomy_path, "r", encoding="utf-8") as f:
        taxonomy = json.load(f)
    return taxonomy

def annotate_with_taxonomy(text, taxonomy):
    """
    Analyse un texte et retourne un dictionnaire de tags trouvés
    en fonction de la taxonomie hiérarchique fournie.
    """
    tags_found = {}

    # Normaliser le texte pour la recherche (minuscules, sans accents si besoin)
    text_lower = text.lower()

    for category, subcategories in taxonomy.items():
        for subcat, keywords in subcategories.items():
            for keyword in keywords:
                # Recherche insensible à la casse et au pluriel approximatif
                if re.search(r"\b" + re.escape(keyword.lower()) + r"s?\b", text_lower):
                    # Si trouvé, on associe le tag à la catégorie
                    tags_found[category] = subcat
                    break  # Passe au sous-tag suivant
            if category in tags_found:
                break  # Si une correspondance trouvée pour cette catégorie, on arrête

    return tags_found

# --- Exemple d'utilisation ---
if __name__ == "__main__":
    taxonomy = load_taxonomy("config/taxonomie.json")
    
    sample_text = """
    Ce projet de migration cloud pour une banque commerciale inclut
    l'implémentation d'une infrastructure réseau sécurisée dans un datacenter.
    """
    
    tags = annotate_with_taxonomy(sample_text, taxonomy)
    print("Tags détectés :", tags)
