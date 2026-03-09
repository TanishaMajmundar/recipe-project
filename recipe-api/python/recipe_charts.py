import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client.get_database("Recipe")  # Adjust if your DB name differs

# Setup correct chart output path
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
charts_path = os.path.join(base_dir, "frontend", "charts")
os.makedirs(charts_path, exist_ok=True)

# Helper function for consistent colors
def get_coolwarm_colors(n):
    return sns.color_palette("coolwarm", n)

# Fetch recipes
recipes_cursor = db.Full_Recipe.find()
recipes = pd.DataFrame(list(recipes_cursor))

# Skip if no recipes found
if recipes.empty:
    print("No recipe data found.")
    exit()

# 1. Recipes by Dish Type
dish_counts = recipes['Dish Type'].value_counts()
plt.figure(figsize=(8, 8))
colors = get_coolwarm_colors(len(dish_counts))
plt.pie(
    dish_counts.values,
    labels=dish_counts.index,
    autopct='%1.1f%%',
    startangle=140,
    colors=colors
)
plt.title('Recipes by Dish Type')
plt.axis('equal')
plt.tight_layout()
plt.savefig(os.path.join(charts_path, "recipes_by_dish_type.png"))
plt.show()

# 2. Average Prep Time by Dish Type
avg_prep_time = recipes.groupby('Dish Type')['Total Time'].mean().sort_values()
plt.figure(figsize=(8, 5))
colors = get_coolwarm_colors(len(avg_prep_time))
avg_prep_time.plot(kind='barh', color=colors)
plt.title('Avg Total Time by Dish Type')
plt.xlabel('Minutes')
plt.tight_layout()
plt.savefig(os.path.join(charts_path, "avg_total_time_by_dishtype.png"))
plt.show()

# 3. Total Time Distribution
plt.figure(figsize=(8, 5))
sns.histplot(recipes['Total Time'], bins=15, kde=True, color=get_coolwarm_colors(1)[0])
plt.title('Total Time Distribution')
plt.xlabel('Total Time (mins)')
plt.ylabel('Number of Recipes')
plt.tight_layout()
plt.savefig(os.path.join(charts_path, "total_time_distribution.png"))
plt.show()