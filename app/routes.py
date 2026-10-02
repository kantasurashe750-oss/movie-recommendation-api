import os

from flask import Flask, jsonify, request

from app.recommender import MovieRecommender


def create_app():
    app = Flask(__name__)

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_path = os.path.join(base_dir, "model", "model.pkl")

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}. Train the model before starting the API.")

    recommender = MovieRecommender.load(model_path)

    @app.get("/")
    def home():
        return jsonify({
            "message": "Movie Recommendation API",
            "endpoints": {
                "health": "/health",
                "recommend": "/recommend?movie=Avatar"
            }
        })

    @app.get("/health")
    def health():
        return jsonify({
            "status": "ok",
            "service": "movie-recommendation-api"
        })

    @app.get("/recommend")
    def recommend():
        movie = request.args.get("movie", "").strip()

        if not movie:
            return jsonify({
                "error": "movie query parameter is required"
            }), 400

        try:
            recommendations = recommender.recommend(movie)
            return jsonify({
                "movie": movie,
                "recommendations": recommendations
            })
        except ValueError as exc:
            return jsonify({
                "error": str(exc)
            }), 404

    return app
