# Automatic food calories estimation from images

## Problem Statement

Our first observation was that it's very hard for people to estimate the calories in a meal. We want to make this easier by providing an automatic way to estimate the calories for individuals and their health professionals and provide an interface for monitoring nutrition-based health.

## Goal

Through this project, our goal is to support health professional who need to monitor their patients nutritional health between consultations.

Here are some patients typologies who could benefit from our work:
- pregnant mothers
- patients diagnosed with diabetes in order to dynamically adjust their daily insuline intake.
- patients needing scientific monitoring of calories intake, either for gain or loss of weight
- iron-deficient patients

Apart from that, this project could benefit:
- people who wish to monitor their nutrition, for example athletes who need to monitor protein intake or fat consumption.
- anyone interested in better understanding their nutritional habits.

# Try the interface

## Install uv
Run
`curl -LsSf https://astral.sh/uv/install.sh | sh`

Then, run: `uv sync`

Finally, activate your environment using: `source .venv/bin/activate`

## Create your .env file

you can do `touch .env` and then `vim .env` to edit your secrets and add your Scaleway API KEY with the following format:
`SCW_SECRET_KEY="xxxx"`

## Initialize alembic

Run `alembic upgrade head` to setup the database schema

## Populate the database

Run `python src/travai/backend/db_populate.py`

## Setup the vector db

Run `python src/travai/backend/vector_db/vector_database.py`

## Run the app

To run the app, use: `streamlit run src/travai/app/run.py`

## How to use the app

Once in the app, feel free to join an account locally using those test credentials:

- Username: `emma@example.com`
- Password: `hashed_password3`

## Submitting a food picture

Click on the file uploader once logged in, pick your favorite plate and let the magic begin!
Once the picture is uploaded, tap the `Analyze Image` button to run computations.

## Adjusting model predictions

Our model can definitely be wrong, make sure to carefully review the model output, you can easily change fields.

## Submit your journal item

Once everything is right, click "Save to journal" to add it to the user database.

## Monitor calories intake per meal

On the `History` tab, you can visualize a dashboard showcasing things such as:
- calorie intake per meal through time
- success metrics on the diet
- detailed meal breakdown (per-ingredient detail)
