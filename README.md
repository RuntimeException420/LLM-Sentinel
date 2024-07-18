# LLM-Sentinel

## API Setup
1. Create an Anthropic API Key
2. In Windows, define a new Environment Variable, Name: `ANTHROPIC_API_KEY`, Value: `[YOUR_API_KEY]`
3. Restart PC
4. The script will then retrieve your API key from the machine's environment variables

## Office2JSON Setup
1. Clone https://github.com/RuntimeException420/Office2JSON to your PC
2. In Windows, open your Environment Variables
3. Add to or, if not existent, create the system variable, Name: `PYTHONPATH`, Value: `[PATH_TO\Office2JSON\src]`
4. LLM-Sentinel can now import Office2JSON

## Usage
`python3 LLM-Sentinel.py [file]`