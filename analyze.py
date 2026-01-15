# from sympy import content
from dotenv import load_dotenv
load_dotenv()
import json
import os
from typing import Any, Dict
from litellm import completion
import json
from jsonschema import validate, ValidationError

# You can replace these with other models as needed but this is the one we suggest for this lab.
MODEL = "groq/llama-3.3-70b-versatile"

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
   raise RuntimeError("GROQ_API_KEY environment variable not set")
os.environ["GROQ_API_KEY"] = api_key

ITINERARY_SCHEMA = {
    "type": "object",
    "properties": {
        "destination": {"type": "string"},
        "price_range": {"type": "string"},
        "ideal_visit_times": {"type": "array", "items": {"type": "string"}},
        "top_attractions": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["destination", "price_range", "ideal_visit_times", "top_attractions"],
    "additionalProperties": False,
}


def get_itinerary(destination: str) -> Dict[str, Any]:
    """
    Returns a JSON-like dict with keys:
      - destination
      - price_range
      - ideal_visit_times
      - top_attractions
    """
    resp = completion(
      model=MODEL,
      messages=[
          {
              "role": "system",
              "content": (
                  "You are an API that returns STRICT JSON only. "
                  "No markdown, no code fences, no extra keys, no commentary."
              ),
          },
          {
              "role": "user",
              "content": (
                  f'Create a travel summary for destination="{destination}".\n'
                  "Return a JSON object that matches this schema exactly:\n"
                  "- destination: string (must equal the destination input)\n"
                  "- price_range: string (one of: budget | medium | luxury)\n"
                  "- ideal_visit_times: array of strings\n"
                  "- top_attractions: array of strings\n"
                  "Return ONLY the JSON object."
              ),
          },
      ],
      response_format={
          "type": "json_schema",
          "json_schema": {
              "name": "travel_itinerary",
              "schema": ITINERARY_SCHEMA,
              "strict": True,
          },
      },
      temperature=0.2,
  )
    content = resp["choices"][0]["message"]["content"]

    if isinstance(content, dict):
      data = content
    elif isinstance(content, str):
        data = json.loads(content)  
    else:
       raise ValueError(f"Unexpected response content type: {type(content)}")
    try:
        validate(instance=data, schema=ITINERARY_SCHEMA)
    except ValidationError as e:
        raise ValueError(f"Response does not match schema: {e.message}")
    return data


    
  
    
