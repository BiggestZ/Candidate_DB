import json
from pydantic import BaseModel, ValidationError

class LLMResponseError(Exception):
    pass

def parse_llm_json(response: str, schema: type[BaseModel]) -> BaseModel:
    """
    Validates / parses LLM Json output into a Pydantic Model
    """
    try:
        # Remove whitespace
        response = response.strip()
        # Ensure valid JSON
        data = json.loads(response)
        # Validate schema
        return schema.model_validate(data)
    
    # Exception 1: LLM output is a malformed
    except json.JSONDecodeError as e:
        raise LLMResponseError(f"Invalid JSON returned by LLM: {e}")
    # Exception 2: LLM output is a JSON, but fails pydantic model validation
    except ValidationError as e:
        raise LLMResponseError(f"LLM output failed schema validation: {e}")
