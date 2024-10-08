import json
import anthropic
import os
import Office2JSON
import argparse
import time
import zipfile
import shutil

MAX_TOKEN_COUNT = 200000  # current max token context window size; check Anthropic docs for updates

if __name__ == "__main__":
    rel_path = ".\\"
    try:
        args_parser = argparse.ArgumentParser("LLM-Sentinel.py")
        args_parser.add_argument("file",
                                 help="Provide the file path to a Microsoft Office document to be analysed")
        args_parser.add_argument('-j', '--json',
                                 action='store_true',
                                 help="Provide a previously extracted JSON file, instead of an OOXML document. "
                                      "Helpful for testing different file adjustments.")
        args_parser.add_argument('-v', '--verbose',
                                 action='store_true',
                                 help="Detailed static analysis, with an increased amount of output tokens. Creates an "
                                      ".xml file")
        args = args_parser.parse_args()

        rel_path, file = os.path.split(args.file)
        if args.json:
            if not args.file.endswith(".json"):
                raise FileNotFoundError("Make sure to provide the extraction in a JSON formatted file. See "
                                        "'LLM-Sentinel.py -h' for help.")
            extraction_time = 0
            with open(args.file) as content:
                JSON_CONTENT = content.read()
        else:
            if args.file.endswith(".json"):
                raise FileNotFoundError("Cannot extract JSON file. To send provided extraction, use option -j "
                                        "or --json. See 'LLM-Sentinel.py -h' for help.")
            start_time = time.time()
            Office2JSON.extract(args)
            extraction_time = time.time() - start_time

            with open(os.path.join(rel_path, "extracted_" + file + ".json")) as content:  # created by Office2JSON
                JSON_CONTENT = content.read()

        prompt_ver = "../assets/prompt_verbose.txt" if args.verbose else "../assets/prompt.txt"
        with open(prompt_ver) as prompt:
            PROMPT = prompt.read()

        client = anthropic.Anthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY")
        )
        token_count = client.count_tokens(JSON_CONTENT) + client.count_tokens(PROMPT)

        if token_count > MAX_TOKEN_COUNT:
            print(f"Unable to send {token_count}, exceeding the current maximum of {MAX_TOKEN_COUNT} "
                  f"tokens in a request.\n"
                  f"Check the Anthropic documentation for updates.")
            raise InterruptedError
        proceed = ""
        while not proceed == "yes" and not proceed == "no":
            proceed = input(f"{token_count} tokens will be sent to Anthropic API. Want to continue? 'yes' | 'no' - ")
        if proceed == "no":
            raise InterruptedError

        request_start_time = time.time()
        message = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=4000 if args.verbose else 200,
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
        if args.json:
            file = file.replace("extracted_", "")  # to keep the original naming theme
        if args.verbose:
            data = message.to_json()
            data = json.loads(data)
            xml_content = data['content'][0]['text']
            with open(os.path.join(rel_path, "response-verbose_" + file + ".xml"), 'w', encoding='utf-8') as f:
                f.write(xml_content)
        else:
            with open(os.path.join(rel_path, "response_" + file + ".json"), "w", encoding="utf-8") as res:
                res.write(message.to_json(indent=4))

        print(40 * "_")
        print(f"Extraction time: \t{round(extraction_time, 3)} seconds")
        print(f"Extraction path: \t{rel_path}")
        print("|" + 18 * " -")
        print(f"Response time: \t\t{round(time.time() - request_start_time, 3)} seconds")
        print(f"Response path: \t\t{rel_path}")
        print(40 * "_")

    except InterruptedError:
        print("Process interrupted by user, exiting...")
    # Errors from Office2JSON
    except FileNotFoundError as e:
        print("File was not found.\n")
        print(e)
    except shutil.SameFileError as e:
        print("Error occurred.\n")
        print(e)
    except zipfile.BadZipfile as e:
        print("Can't open file as archive. File may be of an OLE format, rather than OOXML format.\n")

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
