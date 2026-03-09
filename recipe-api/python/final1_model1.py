import pymongo
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.neighbors import NearestNeighbors
import json
import sys
from dotenv import load_dotenv
import os

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
client = pymongo.MongoClient(MONGO_URI)
db = client["Recipe"]  
collection = db["Full_Recipe"]   

recipes = list(collection.find({}, {"_id": 0, "Recipe Name": 1, "INGREDIENTS": 1}))
ignore = ['salt', 'water']

def process(ingredients):
    return ', '.join([
        ing.strip().lower()
        for ing in ingredients.split(", ")
        if ing.strip().lower() not in ignore
    ])
recipe_names = [recipe["Recipe Name"] for recipe in recipes]
cleaned_ingredients = [process(recipe["INGREDIENTS"]) for recipe in recipes]

vectorizer = CountVectorizer(tokenizer=lambda x: x.split(', '))
matrix = vectorizer.fit_transform(cleaned_ingredients)

model = NearestNeighbors(n_neighbors=10, metric='cosine')
model.fit(matrix)

user_input = sys.argv[1].lower().split(",")
user_vector = vectorizer.transform([', '.join(user_input)])
distances, indices = model.kneighbors(user_vector)
recommended_recipes = [recipe_names[i] for i in indices[0]]
print(json.dumps(recommended_recipes))