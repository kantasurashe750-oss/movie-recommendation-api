from __future__ import annotations

import pickle
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class MovieRecommender:
    def __init__(self):
        self.dataset = None
        self.titles = None
        self.similarity_matrix = None
        self.vectorizer = None

    def load_dataset(self, csv_path):
        self.dataset = pd.read_csv(csv_path)

        if "title" not in self.dataset.columns or "description" not in self.dataset.columns:
            raise ValueError("Dataset must contain 'title' and 'description' columns.")

        self.titles = self.dataset["title"].tolist()
        return self

    def train(self):
        if self.dataset is None:
            raise ValueError("Load a dataset before training the model.")

        text_data = self.dataset["description"].fillna("").tolist()

        self.vectorizer = TfidfVectorizer(stop_words="english")
        tfidf_matrix = self.vectorizer.fit_transform(text_data)
        self.similarity_matrix = cosine_similarity(tfidf_matrix)
        return self

    def recommend(self, movie_name: str, top_n: int = 5):
        if self.similarity_matrix is None or self.titles is None:
            raise ValueError("Model is not trained yet. Call 'train()' first.")

        normalized_titles = [title.lower() for title in self.titles]
        normalized_movie = movie_name.strip().lower()

        if normalized_movie not in normalized_titles:
            raise ValueError(f"Movie not found: {movie_name}")

        movie_index = normalized_titles.index(normalized_movie)
        scores = list(enumerate(self.similarity_matrix[movie_index]))
        scores = sorted(scores, key=lambda item: item[1], reverse=True)
        scores = [item for item in scores if item[0] != movie_index][:top_n]

        return [self.titles[index] for index, _ in scores]

    def save(self, file_path):
        storage = {
            "titles": self.titles,
            "similarity_matrix": self.similarity_matrix,
            "vectorizer": self.vectorizer,
        }

        with open(file_path, "wb") as model_file:
            pickle.dump(storage, model_file)

    @classmethod
    def load(cls, file_path):
        with open(file_path, "rb") as model_file:
            storage = pickle.load(model_file)

        recommender = cls()
        recommender.titles = storage["titles"]
        recommender.similarity_matrix = storage["similarity_matrix"]
        recommender.vectorizer = storage["vectorizer"]
        return recommender


if __name__ == "__main__":
    data_path = Path("data/movies.csv")
    model_path = Path("model/model.pkl")

    recommender = MovieRecommender().load_dataset(str(data_path)).train()
    recommender.save(str(model_path))

    print(f"Model saved to: {model_path}")
    print("Sample recommendations for 'Avatar':")
    print(recommender.recommend("Avatar"))
