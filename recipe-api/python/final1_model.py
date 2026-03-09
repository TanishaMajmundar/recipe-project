import pymongo
import json
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

# Connect to MongoDB
client = pymongo.MongoClient(MONGO_URI)
db = client["Recipe"]
collection = db["Full_Recipe"]

# Fetch recipes
recipes = list(collection.find({}, {"_id": 0, "Recipe Name": 1, "INGREDIENTS": 1}))

# Get user input ingredients from command line
user_input = sys.argv[1].lower().split(",")
user_ingredients = set(i.strip() for i in user_input)

# Compare and rank recipes based on matching ingredients
results = []

for recipe in recipes:
    recipe_name = recipe["Recipe Name"]
    ingredients_list = recipe["INGREDIENTS"].lower().split(",")
    recipe_ingredients = set(i.strip() for i in ingredients_list)
    
    match_count = len(user_ingredients & recipe_ingredients)
    total_ingredients = len(recipe_ingredients)
    match_ratio = match_count / total_ingredients if total_ingredients else 0
    
    if match_count > 0:
        results.append({
            "name": recipe_name,
            "match_count": match_count,
            "total_ingredients": total_ingredients,
            "match_ratio": match_ratio
        })

# Sort by match count, then match ratio
results = sorted(results, key=lambda x: x["match_ratio"], reverse=True)

# Debug to stderr
print("DEBUG: Matching recipes with ratio\n", file=sys.stderr)
for r in results[:10]:
    print(f"{r['name']}: {r['match_count']} out of {r['total_ingredients']} matched ({r['match_ratio']:.2f})", file=sys.stderr)

# Final output — can be just names, or full info
# Uncomment the one you want:

# Option 1: Only names (default API style)
# final_output = [r["name"] for r in results[:10]]

# Option 2: Include match stats (better for frontend insight)
final_output = [
    {
        "name": r["name"],
        "matches": f"{r['match_count']} out of {r['total_ingredients']}",
        "match_ratio": round(r["match_ratio"], 2)
    }
    for r in results[:10]
]

# Output JSON
print(json.dumps(final_output))
