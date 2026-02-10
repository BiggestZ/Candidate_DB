# This file will test intent detection using pre-set input

from openai import OpenAI
import os, sys
# Go to root
project_root=os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
#print(project_root)
sys.path.insert(0, project_root)

from Chatbot.gen_ai.intent.intent_router import detect_intent

def test_intent(user_message: str) -> dict:
    # DEBUG: Print the actual prompt being sent
    # print("=== PROMPT SENT ===")
    # print(user_message)
    # print("=== END PROMPT ===")
    return detect_intent(user_message)

# Print Statements
print (test_intent("Find me a candidate"))
#print (test_intent("Hello!"))