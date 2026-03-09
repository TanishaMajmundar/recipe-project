import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client.get_database("Recipe")  

base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
charts_path = os.path.join(base_dir, "frontend", "charts")
os.makedirs(charts_path, exist_ok=True)

def get_coolwarm_colors(n):
    return sns.color_palette("coolwarm", n)

users_cursor = db.users.find()
users = pd.DataFrame(list(users_cursor))

if users.empty:
    print("No user data found.")
    exit()

# 1. Gender Distribution
gender_counts = users['gender'].value_counts()
plt.figure(figsize=(5, 5))
colors = get_coolwarm_colors(len(gender_counts))
plt.pie(gender_counts, labels=gender_counts.index, autopct='%1.1f%%', startangle=140,
        wedgeprops={'width': 0.5}, colors=colors)
plt.title('Gender Distribution')
plt.savefig(os.path.join(charts_path, "gender_distribution.png"))
plt.show()

# 2. Age Distribution
plt.figure(figsize=(7, 5))
sns.histplot(users['age'], bins=[10, 20, 30, 40, 50, 60, 70], kde=False, color=get_coolwarm_colors(1)[0])
plt.title('Age Distribution')
plt.xlabel('Age Groups')
plt.ylabel('Number of Users')
plt.tight_layout()
plt.savefig(os.path.join(charts_path, "age_distribution.png"))
plt.show()

# 3. Food Preference
food_counts = users['food'].value_counts()
plt.figure(figsize=(5, 5))
colors = get_coolwarm_colors(len(food_counts))
plt.pie(food_counts, labels=food_counts.index, autopct='%1.1f%%', startangle=140, colors=colors)
plt.title('Food Preference')
plt.savefig(os.path.join(charts_path, "food_preference.png"))
plt.show()

# 4. Users by Age & Gender
bins = [10, 20, 30, 40, 50, 60, 70]
labels = ['10-20', '21-30', '31-40', '41-50', '51-60', '61-70']
users['AgeGroup'] = pd.cut(users['age'], bins=bins, labels=labels, right=False)
age_gender_data = users.groupby(['AgeGroup', 'gender']).size().unstack(fill_value=0)
colors = get_coolwarm_colors(len(age_gender_data.columns))
age_gender_data.plot(kind='bar', stacked=True, color=colors)
plt.title('Users by Age Group and Gender')
plt.xlabel('Age Group')
plt.ylabel('Number of Users')
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(os.path.join(charts_path, "users_by_age_gender.png"))
plt.show()