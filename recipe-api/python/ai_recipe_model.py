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

recipes = list(collection.find({}, {
    "_id": 1,
    "Recipe Name": 1,
    "INGREDIENTS": 1
}))

# Create lookup dictionary
recipe_lookup = {r["Recipe Name"]: r for r in recipes}

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
match_info = {}

for recipe in recipes:

    name = recipe["Recipe Name"]
    recipe_set = set(clean_ingredients(recipe["INGREDIENTS"]))

    matched = user_set & recipe_set
    missing = recipe_set - user_set

    match_count = len(matched)
    total = len(recipe_set)

    if total == 0:
        continue

    ratio = match_count / total

    # Adaptive filtering
    if user_count == 1:
        if match_count < 1:
            continue
    elif user_count == 2:
        if match_count < 1:
            continue
    else:
        if match_count < 1:
            continue

    match_scores[name] = ratio

    match_info[name] = {
        "match_count": match_count,
        "total_ingredients": total,
        "matched_ingredients": list(matched),
        "missing_ingredients": list(missing)
    }

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

# -----------------------------
# First Pass (Strong Matches)
# -----------------------------
for name, score in top:

    if score >= 0.25:

        recipe_data = recipe_lookup[name]

        results.append({
            "_id": str(recipe_data["_id"]),
            "name": name,
            "score": round(score, 3),
            "match_count": match_info[name]["match_count"],
            "total_ingredients": match_info[name]["total_ingredients"],
            "matched_ingredients": match_info[name]["matched_ingredients"],
            "missing_ingredients": match_info[name]["missing_ingredients"]
        })

    if len(results) == 10:
        break

# -----------------------------
# Second Pass (Fill Remaining)
# -----------------------------
if len(results) < 10:

    for name, score in top:

        if score >= 0.20 and name not in [r["name"] for r in results]:

            recipe_data = recipe_lookup[name]

            results.append({
                "_id": str(recipe_data["_id"]),
                "name": name,
                "score": round(score, 3),
                "match_count": match_info[name]["match_count"],
                "total_ingredients": match_info[name]["total_ingredients"],
                "matched_ingredients": match_info[name]["matched_ingredients"],
                "missing_ingredients": match_info[name]["missing_ingredients"]
            })

        if len(results) == 10:
            break

# -----------------------------
# OUTPUT JSON
# -----------------------------
print(json.dumps(results))