from openai import OpenAI
import os
import base64
from pydantic import BaseModel
import typing as t


class ImageModel(BaseModel):
    """Image model"""

    description: str
    represented_character: t.Literal["man", "woman", "other"]


def get_client():
    """Returns the OpenAI client using SCW_SECRET_KEY and SCW_DEFAULT_PROJECT_ID present in the .env file

    Returns
    -------
    OpenAI
        The OpenAI client
    """
    return OpenAI(
        base_url=f"https://api.scaleway.ai/{os.getenv('SCW_DEFAULT_PROJECT_ID')}/v1",
        api_key=os.getenv(
            "SCW_SECRET_KEY"
        ),  # Replace SCW_SECRET_KEY with your IAM API key
    )


def b64_from_path(image_path: str) -> str:
    """Encodes an image file to base64 string

    Parameters
    ----------
    image_path : str
        The image path

    Returns
    -------
    str
        The b64-encoded representation of the image
    """
    with open(image_path, "rb") as image_file:
        base64_string = base64.b64encode(image_file.read()).decode("utf-8")
    return base64_string


def get_structured_answer(
    client: OpenAI,
    model_name: str,
    prompt: str,
    base64_image: str,
    response_format: BaseModel,
) -> str:
    """Generates answer with client using model_name, a prompt and the base64 representation of the image

    Parameters
    ----------
    client : OpenAI
        the OpenAI client
    model_name : str
        model handle
    prompt : str
        text prompt used for the model
    base64_image : str
        b64-encoded image
    response_format: BaseModel
        the BaseModel-inheriting class to use for structured outputs generation.

    Returns
    -------
    str
        The BaseModel instance as str
    """
    return client.beta.chat.completions.parse(
        model=model_name,
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}",
                        },
                    },
                ],
            },
        ],
        max_tokens=None,
        temperature=1.0,
        top_p=1,
        presence_penalty=0,
        response_format=response_format,
    ).choices[0].message.content


def main() -> None:
    client = get_client()
    b64_image = b64_from_path("/Users/raphael/TravAI/1.png")
    response = get_structured_answer(
        client=client,
        model_name="pixtral-12b-2409",
        prompt="Describe the Meal present in the image",
        base64_image=b64_image,
        response_format=ImageModel,
    )
    print(response)
    return


if __name__ == "__main__":
    main()
