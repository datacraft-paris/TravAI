# Automatic food calories estimation from images

## Problem Statement

Our first observation was that it's very hard for people to estimate the calories in a meal. We want to make this easier by providing an automatic way to estimate the calories for individuals and their health professionals and provide an interface for monitoring nutrition-based health.

### Install uv
Run
`curl -LsSf https://astral.sh/uv/install.sh | sh`

Then, run: `uv sync`

Finally, activate your environment using: `source .venv/bin/activate`

## Run the app

To run the app, use: `streamlit run src/travai/app/run.py`