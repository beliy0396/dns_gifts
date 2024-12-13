import pandas as pd
import numpy as np
from flask import Flask, render_template, request, jsonify
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle

app = Flask(__name__)

# Load the DataFrame and pipeline *outside* the function for efficiency
df = pd.read_excel('data.xlsx')  #Make sure data.xlsx is in the same directory as your flask app
with open('pipeline.pkl', 'rb') as file:
    pipeline = pickle.load(file)


def get_recommendations(user_group, user_price_category, df):
    try:
        if user_group == 'Все':
            combined_recommendations = df[df['Ценовая категория'] == user_price_category]
        else:
            new_data = pd.DataFrame({'Группа': [user_group], 'Ценовая категория': [user_price_category]})
            predicted_category = pipeline.predict(new_data)[0]
            recommendations = df[(df['Категория'] == predicted_category) &
                                 (df['Группа'] == user_group) &
                                 (df['Ценовая категория'] == user_price_category)]
            recommendations_all = df[(df['Группа'] == 'Все') & (df['Ценовая категория'] == user_price_category)]
            combined_recommendations = pd.concat([recommendations, recommendations_all]).drop_duplicates()

        num_recommendations = min(5, len(combined_recommendations))
        random_indices = np.random.choice(len(combined_recommendations), num_recommendations, replace=False)
        random_recommendations = combined_recommendations.iloc[random_indices][['Название', 'Рейтинг', 'Цена', 'Ссылка']]
        return random_recommendations.to_dict('records') # Convert to list of dictionaries for JSON
    except (KeyError, IndexError, ValueError) as e:
        return [{'error': str(e)}] # Return error as a dictionary



@app.route("/", methods=["GET", "POST"])
def index():
    recommendations = []
    if request.method == "POST":
        user_group = request.form.get("user_group")
        user_price_category = request.form.get("user_price_category")
        recommendations = get_recommendations(user_group, user_price_category, df)
    return render_template("index.html", user_groups=["Ребёнок", "Мужчина", "Женщина", "Все"],
                           user_price_categories=["Дешёвый", "Средний", "Дорогой"],
                           recommendations=recommendations)


if __name__ == "__main__":
    app.run(debug=True)