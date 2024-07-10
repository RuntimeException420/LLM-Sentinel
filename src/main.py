import anthropic
import os

with open("../assets/extracted_information.txt") as content:
    JSON_CONTENT = content.read()

with open("../assets/prompt.txt") as prompt:
    PROMPT = prompt.read()

client = anthropic.Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY")
)

# Replace placeholders like {{JSON_CONTENT}} with real values,
# because the SDK does not support variables.
message = client.messages.create(
    model="claude-3-5-sonnet-20240620",
    max_tokens=1000,
    temperature=0,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": PROMPT
                }
            ]
        }
    ]
)

# #
# TODO: --verbose mode with different prompt and more output for static analysis
#
# TODO: check for response Headers (see Anthropic docs /en/api/rate-limits)
# #

if __name__ == "__main__":
    print(message)
