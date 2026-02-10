from pathlib import Path
from jinja2 import Template
from typing import List

# Access the prompts folder
PROMPT_ROOT = Path("Chatbot/gen_ai/prompts")
#print(PROMPT_ROOT)

# *args: collects extra positional arguments into tuple
# **kwargs: Collects keyword args into dict

def load_prompt(path: str, **kwargs) -> str:
    template_path = PROMPT_ROOT / path # set up path: "prompts/['path']"
    template_text = template_path.read_text() # Reads in the path
    template = Template(template_text) # Stores path in template
    # print("=== PROMPT ===")
    # print(template_text)
    # print("=== END PROMPT ===")
    return template.render(**kwargs) # Renders Template

def load_keywords(filename: str) -> List[str]:
    """Load keywords in from 'search_keywords.txt' """
    filepath = PROMPT_ROOT / filename
    keywords=[]

    with open(filepath, 'r') as file:
        for line in file: 
            line = line.strip()
            # Skip empty lines / comments
            if line and not line.startswith('#'):
                keywords.append(line.lower())
    return keywords



# Test that it loads the prompt
# if __name__ == "__main__":
#    load_prompt("intent/intent.txt")