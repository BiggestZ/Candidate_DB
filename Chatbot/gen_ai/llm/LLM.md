* base.py: generic class designed to be plug and play with any LLM Model

* client.py: Like base.py, but implements the function from `router.py` to allow the user to pick which LLM to use.

* config.py: Holds configurations for LLMs based on intent, as well as defines LLM Task for checking Intent, and LLMProvider to see which LLM between OpenAI, Gemini, and Anthropic the use selected for future use.

* prompt_loader.py: Designed to load in prompts from prompts/. Has 2 functions, 1 to load in prompts, the other loads in keywords (intent/search_keywords.txt) to help with intent classification.

* response_parser.py: This file will read LLM output and validate it against the pydantic models.

* router.py: Designed to route to different LLMs (OpenAI, Claude, etc) based on user choice, to allow for free change when desired (FUTURE)