import anthropic
import os
import Office2JSON
import argparse
import time
import zipfile
import shutil


if __name__ == "__main__":
    rel_path = ".\\"
    try:
        args_parser = argparse.ArgumentParser("LLM-Sentinel.py")
        args_parser.add_argument("file", help="Provide the file path to a Microsoft Office document to be analysed.")
        args = args_parser.parse_args()

        start_time = time.time()
        Office2JSON.extract(args)
        extraction_time = time.time() - start_time

        request_start_time = time.time()
        rel_path, file = os.path.split(args.file)
        with open(os.path.join(rel_path, "extracted_" + file + ".json")) as content:  # created by Office2JSON
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

        with open(os.path.join(rel_path, "response_" + file + ".json"), "w", encoding="utf-8") as res:
            res.write(message.to_json(indent=4))

        print(40 * "_")
        print(f"Extraction time: \t{round(extraction_time, 3)} seconds")
        print(f"Extraction path: \t{rel_path}")
        print(" |" + 18 * " -")
        print(f"Extraction time: \t{round(time.time() - request_start_time, 3)} seconds")
        print(f"Extraction path: \t{rel_path}")
        print(40 * "_")

    # Errors from Office2JSON
    except FileNotFoundError as e:
        print("File was not found.\n" + e)
    except shutil.SameFileError as e:
        print("Error occurred.\n" + e)
    except zipfile.BadZipfile as e:
        print("Can't open file as archive.\n")

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
    finally:
        # clean-up
        file = os.path.join(rel_path, "temp_extraction")
        if os.path.exists(file):
            shutil.rmtree(file)

# #
# TODO: --verbose mode with different prompt and more output for static analysis
# #

