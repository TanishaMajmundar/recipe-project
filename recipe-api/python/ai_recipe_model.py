import pymongo
import json
import sys
import os
from dotenv import load_dotenv
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.neighbors import NearestNeighbors

# -----------------------------
# Load MongoDB
# -----------------------------
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

client = pymongo.MongoClient(MONGO_URI)
db = client["Recipe"]
collection = db["Full_Recipe"]

recipes = list(collection.find({}, {"_id": 0, "Recipe Name": 1, "INGREDIENTS": 1}))

# -----------------------------
# Ignore common ingredients
# -----------------------------
ignore = {"salt", "water", "oil", "sugar", "pepper"}

# -----------------------------
# Clean ingredients
# -----------------------------
def clean_ingredients(ingredients):
    return [
        ing.strip().lower()
        for ing in ingredients.split(",")
        if ing.strip().lower() not in ignore
    ]

recipe_names = []
cleaned_recipes = []

for r in recipes:
    recipe_names.append(r["Recipe Name"])
    cleaned_recipes.append(", ".join(clean_ingredients(r["INGREDIENTS"])))

# -----------------------------
# ML MODEL
# -----------------------------
vectorizer = CountVectorizer(
    tokenizer=lambda x: x.split(", "),
    token_pattern=None
)

matrix = vectorizer.fit_transform(cleaned_recipes)

model = NearestNeighbors(n_neighbors=20, metric="cosine")
model.fit(matrix)

# -----------------------------
# USER INPUT
# -----------------------------
if len(sys.argv) < 2:
    print(json.dumps({"error": "No ingredients provided"}))
    sys.exit()

user_input = [i.strip().lower() for i in sys.argv[1].split(",")]
user_set = set(user_input)
user_count = len(user_set)

# -----------------------------
# INGREDIENT MATCHING
# -----------------------------
match_scores = {}

for recipe in recipes:

    name = recipe["Recipe Name"]
    recipe_set = set(clean_ingredients(recipe["INGREDIENTS"]))

    match_count = len(user_set & recipe_set)
    total = len(recipe_set)

    if total == 0:
        continue

    ratio = match_count / total

    # -----------------------------
    # Adaptive filtering
    # -----------------------------
    if user_count == 1:
        if match_count < 1:
            continue

    elif user_count == 2:
        if match_count < 1:
            continue

    else:
        if match_count < 2 or ratio < 0.3:
            continue

    match_scores[name] = ratio

# -----------------------------
# ML SIMILARITY
# -----------------------------
user_vector = vectorizer.transform([", ".join(user_input)])
distances, indices = model.kneighbors(user_vector)

ml_scores = {}

for dist, idx in zip(distances[0], indices[0]):
    recipe = recipe_names[idx]
    similarity = 1 - dist
    ml_scores[recipe] = similarity

# -----------------------------
# COMBINE SCORES
# -----------------------------
final_scores = {}

for recipe in match_scores:

    match_score = match_scores.get(recipe, 0)
    ml_score = ml_scores.get(recipe, 0)

    score = (0.7 * match_score) + (0.3 * ml_score)

    final_scores[recipe] = score

# -----------------------------
# SORT RESULTS
# -----------------------------
top = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)

results = []

# First pass (strong matches)
for name, score in top:
    if score >= 0.25:
        results.append({
            "name": name,
            "score": round(score,3)
        })
    if len(results) == 10:
        break

# Second pass if less recipes
if len(results) < 10:
    for name, score in top:
        if score >= 0.20 and name not in [r["name"] for r in results]:
            results.append({
                "name": name,
                "score": round(score,3)
            })
        if len(results) == 10:
            break
# -----------------------------
# OUTPUT
# -----------------------------
print(json.dumps(results))