import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv(Path(__file__).with_name(".env"))

BASE_URL = os.getenv("BASE_URL", "http://localhost:1234/v1").strip()
API_KEY = os.getenv("API_KEY", "lm-studio").strip()
MODEL = os.getenv("MODEL", "local-model").strip()
LANG_FROM = os.getenv("LANG_FROM", "English").strip()
LANG_TO = os.getenv("LANG_TO", "Norwegian").strip()
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.5"))

client = OpenAI(
    base_url=BASE_URL,
    api_key=API_KEY,
)


def generate_exercise(
    level: int,
    exercise_type: str,
    lang_from: str = LANG_FROM,
    lang_to: str = LANG_TO,
):
    """
    Generates a language learning exercise using the local AI model.
    
    Parameters:
    - level (int): 1 to 15
    - exercise_type (str): "matching", "single_word_translation", "translation", or "fill_in_blank"
    - lang_from (str): The language of the prompt/question
    - lang_to (str): The target language to learn
    
    Returns:
    - dict: The parsed JSON response from the model, or None if it failed.
    """
    
    # 1. Define the System Prompt (Strict identity)
    system_prompt = (
        "You are a JSON API for a language learning app. "
        "You must ONLY output raw JSON. Do NOT write Python scripts. "
        "Do NOT use markdown code blocks. Do NOT explain your answer. "
        "Use double quotes for all JSON keys and string values; single quotes are invalid."
    )

    # 2. Build the User Prompt based on the requested exercise type
    if exercise_type == "matching":
        prompt = (
            f"Generate a level {level} matching pairs exercise for {lang_to}. "
            f"Return only valid JSON. Each pair must be an array of exactly two strings. "
            f"Separate pair arrays with commas and use double quotes only. "
            f"You MUST use this exact JSON structure: "
            f'{{"exercise_type": "matching", "pairs": [["{lang_from} word", "{lang_to} word"], ["{lang_from} word", "{lang_to} word"]]}}'
        )
        
    elif exercise_type == "single_word_translation":
        prompt = (
            f"Generate a level {level} single-word translation exercise from {lang_from} to {lang_to}. "
            f"The question MUST be exactly one word in {lang_from}, not a phrase or sentence. "
            f"The answer MUST be exactly one word in {lang_to}. "
            f"You MUST use this exact JSON structure: "
            f'{{"exercise_type": "single_word_translation", "question": "{lang_from} word", "answer": "{lang_to} word", "hint": "..."}}'
        )
        
    elif exercise_type == "translation":
        prompt = (
            f"Generate a level {level} translation exercise from {lang_from} to {lang_to}. "
            f"The 'question' MUST be in {lang_from}. The 'answer' MUST be in {lang_to}. "
            f"You MUST use this exact JSON structure: "
            f'{{"exercise_type": "translation", "question": "Translate to {lang_to}: ...", "answer": "...", "hint": "..."}}'
        )
        
    elif exercise_type == "fill_in_blank":
        prompt = (
            f"Generate a level {level} fill_in_blank exercise in {lang_to}. "
            f"The sentence must be very short (MAX 8 words). "
            f"You MUST use this exact JSON structure: "
            f'{{"exercise_type": "fill_in_blank", "sentence_with_blank": "... ___ ...", "answer": "...", "hint": "..."}}'
        )
        
    else:
        raise ValueError(
            "Invalid exercise_type. Choose 'matching', 'single_word_translation', "
            "'translation', or 'fill_in_blank'."
        )

    # 3. Call the local LM Studio API
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=TEMPERATURE,
            max_tokens=300
        )
        
        raw_output = response.choices[0].message.content

        # 4. Clean the output (just in case the model added extra text)
        raw_output = raw_output.replace("```json", "").replace("```", "").strip()
        
        # Extract only the JSON object (from first '{' to last '}')
        start_idx = raw_output.find('{')
        end_idx = raw_output.rfind('}')
        
        if start_idx != -1 and end_idx != -1:
            clean_output = raw_output[start_idx:end_idx+1]
        else:
            clean_output = raw_output

        # 5. Parse and return the JSON
        parsed_json = json.loads(clean_output)
        return parsed_json

    except json.JSONDecodeError:
        print(f"❌ Model failed to return valid JSON. Raw output was:\n{raw_output}")
        return None
    except Exception as e:
        print(f"❌ API Error: {e}")
        return None


# ==========================================
# EXAMPLE USAGE:
# ==========================================
if __name__ == "__main__":
    print("--- Testing Matching ---")
    result1 = generate_exercise(level=2, exercise_type="matching")
    print(json.dumps(result1, indent=2, ensure_ascii=False))

    print("\n--- Testing Translation ---")
    result2 = generate_exercise(level=3, exercise_type="translation", lang_from="Norwegian", lang_to="English")
    print(json.dumps(result2, indent=2, ensure_ascii=False))

    print("\n--- Testing Fill in Blank ---")
    result3 = generate_exercise(level=5, exercise_type="fill_in_blank")
    print(json.dumps(result3, indent=2, ensure_ascii=False))