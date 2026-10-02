# Movie Recommendation API

A beginner-friendly movie recommendation API built with Python, Flask, pandas, and scikit-learn. It recommends movies by comparing their descriptions with TF-IDF vectors and cosine similarity.

## Live demo

- API home: <https://movie-recommendation-api-ynyv.onrender.com/>
- Health check: <https://movie-recommendation-api-ynyv.onrender.com/health>
- Recommendations: <https://movie-recommendation-api-ynyv.onrender.com/recommend?movie=Avatar>

The free Render service may sleep when idle. The first request after inactivity can take longer while it starts.

## Architecture

```text
Movie descriptions (data/movies.csv)
              |
              v
TF-IDF vectors -> cosine similarity -> saved model (model/model.pkl)
                                           |
                                           v
                                    Flask REST API
                                           |
                                           v
                                  Docker container
                                           |
                         GitHub Actions tests on push/PR
                                           |
                    Passing push to main triggers Render deploy
```

Render builds and deploys the service from GitHub. GitHub Actions runs tests and calls a Render deploy hook only after tests pass on `main`. The workflow does not build or push Docker Hub images; Docker is used for local container testing.

## Project structure

```text
app/
  __init__.py       Flask application factory export
  recommender.py    TF-IDF and cosine-similarity recommender
  routes.py         API endpoints
data/
  movies.csv        Movie titles and descriptions
model/
  model.pkl         Saved similarity data and vectorizer
tests/
  test_api.py       API tests
.github/workflows/
  ci-cd.yml         Test and Render deploy workflow
app.py              Local Flask development entry point
wsgi.py             Gunicorn entry point
Dockerfile          Container build instructions
requirements.txt    Python dependencies
.python-version     Render Python version
```

## Run locally

Use Python 3.11. From the repository root:

```bash
python -m venv .venv
```

Activate the environment:

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

```bash
# Linux, macOS, or Git Bash
source .venv/bin/activate
```

Install dependencies, train/save the model if needed, and start Flask:

```bash
python -m pip install -r requirements.txt
python app/recommender.py
python app.py
```

The API listens on <http://localhost:5000>. Keep the terminal running while testing.

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | API information |
| GET | `/health` | Health status |
| GET | `/recommend?movie=Avatar` | Recommend similar movies |

Example success response:

```json
{
  "movie": "Avatar",
  "recommendations": [
    "Titanic",
    "The Dark Knight",
    "The Avengers",
    "Interstellar",
    "Guardians of the Galaxy"
  ]
}
```

Error behavior:

- Missing `movie` parameter: HTTP 400.
- Movie not present in the dataset: HTTP 404.

## Run tests

```bash
python -m pytest -q
```

The test suite covers the home route, health route, successful recommendations, missing input, and unknown movies.

## Run with Docker

Build the image from the repository root:

```bash
docker build -t movie-recommendation-api:local .
```

Run the container on local port 5001 (mapped to the app's port 5000):

```bash
docker run -d --name movie-api-test -p 5001:5000 movie-recommendation-api:local
```

Test it at <http://localhost:5001/health> and <http://localhost:5001/recommend?movie=Avatar>.

Useful commands:

```bash
docker ps
docker logs movie-api-test
docker stop movie-api-test
docker rm movie-api-test
```

## CI/CD and Render

The workflow in `.github/workflows/ci-cd.yml`:

1. Runs tests on pull requests and pushes to `main`.
2. On a push to `main`, triggers Render only if tests pass.

The GitHub repository must have an Actions secret named `RENDER_DEPLOY_HOOK_URL`, containing the Render deploy-hook URL. Keep the hook private. To ensure failed tests block deployment, disable Render's independent auto-deploy and let the workflow trigger deployments.

Render settings used by this app:

- Runtime: Python
- Python version: `3.11.11` (from `.python-version`)
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn --bind 0.0.0.0:$PORT wsgi:app`

## How recommendations work

1. Each movie has a short text description.
2. TF-IDF converts descriptions into weighted numeric vectors. Words that help distinguish one description from the others receive more weight.
3. Cosine similarity compares a movie's vector with the other movie vectors.
4. The recommender sorts by similarity, excludes the selected movie, and returns the top five matches.

This is a small content-based recommender, not a personalized system based on user ratings.

## College demo outline

1. Explain the data, TF-IDF, and cosine similarity.
2. Show `app/recommender.py` and the API routes in `app/routes.py`.
3. Open the live API endpoints above and show the JSON responses.
4. Show the running Docker container with `docker ps`.
5. Show the passing GitHub Actions run and explain that it triggers Render after tests pass.

## Viva questions and short answers

| Question | Short answer |
|---|---|
| What is Flask? | A lightweight Python framework for web applications and APIs. |
| What is an API? | A defined way for software systems to communicate. |
| What is a REST endpoint? | A URL and HTTP method used to access a resource or operation. |
| What is TF-IDF? | A method that weights words by how informative they are in a document compared with a collection. |
| What is cosine similarity? | A measure of how similar two vectors are based on the angle between them. |
| What is Docker? | A platform for packaging and running applications in containers. |
| Image vs. container? | An image is the packaged template; a container is a running instance of it. |
| What is Git? | A version-control tool that tracks code changes. |
| Git vs. GitHub? | Git is the tool; GitHub hosts Git repositories and collaboration features. |
| What is CI/CD? | Automation for checking code and delivering changes. |
| What happens after `git push`? | GitHub Actions runs tests; a passing push to `main` triggers Render to deploy from GitHub. |
| How are deployment secrets protected? | The deploy-hook URL is stored as a GitHub Actions secret, not in the repository. |
| Is the current API on a VPS? | No. It is hosted by Render; local WSL is for development, not a public VPS. |

## Notes

- The sample dataset is intentionally small for learning and demonstration.
- The live API is publicly accessible; do not add private credentials or sensitive data to the repository.
- Render's free service has availability and inactivity limits that may change.
