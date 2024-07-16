import anthropic
import os
import json

if __name__ == "__main__":
    try:
        with open("../assets/extracted_information.json") as content:
            JSON_CONTENT = content.read()

        with open("../assets/prompt.txt") as prompt:
            PROMPT = prompt.read()

        client = anthropic.Anthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY")
        )

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
                            "text": PROMPT.replace("{{JSON_CONTENT}}", JSON_CONTENT)
                        }
                    ]
                }
            ]
        )

        with open("../assets/response.json", "w", encoding="utf-8") as res:
            res.write(message.to_json(indent=4))

    # Error handling inspired by https://github.com/anthropics/anthropic-sdk-python README.md
    except anthropic.APIConnectionError as e:
        print("The server could not be reached")
        print(e.__cause__)  # an underlying Exception, likely raised within httpx.
    except anthropic.RateLimitError as e:
        print("A 429 status code was received; rate limit reached.")
    except anthropic.APIStatusError as e:
        print("Another non-200-range status code was received")
        print(e.status_code)
        print(e.response)
    except FileNotFoundError as e:
        print("File could not be found.")
        print(e)

# #
# TODO: --verbose mode with different prompt and more output for static analysis
# #

