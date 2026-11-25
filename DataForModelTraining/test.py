from openai import OpenAI
import json

# Connect to LM Studio's local server
# (Make sure you clicked "Start Server" in LM Studio and enabled Structured Output)
client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio" # LM Studio ignores this, but the library requires it
)

# The strict system prompt to force JSON
system_prompt = (
    "You are a JSON API for a Norwegian language learning app. "
    "You must ONLY output raw JSON. Do NOT write Python scripts. "
    "If a language is not specified for an exercise, default to Norwegian. "
    "Do NOT use markdown code blocks. Do NOT explain your answer."
)

# Test prompts with STRICT structured formatting
test_prompts = [
    # MATCHING
    "Generate a level 1 matching pairs exercise. You MUST use this exact JSON structure: {\"exercise_type\": \"matching\", \"pairs\": [[\"english\", \"norwegian\"], [\"english\", \"norwegian\"]]}",
    
    "Generate a level 5 matching pairs exercise. You MUST use this exact JSON structure: {\"exercise_type\": \"matching\", \"pairs\": [[\"english\", \"norwegian\"], [\"english\", \"norwegian\"]]}",
    
    # TRANSLATION
    "Generate a level 2 translation exercise from English to Norwegian. You MUST use this exact JSON structure: {\"exercise_type\": \"translation\", \"question\": \"Translate to Norwegian: ...\", \"answer\": \"...\", \"hint\": \"...\"}",
    
    "Generate a level 3 translation exercise from Norwegian to English. You MUST use this exact JSON structure: {\"exercise_type\": \"translation\", \"question\": \"Translate to English: ...\", \"answer\": \"...\", \"hint\": \"...\"}",
    
    "Generate a level 4 translation exercise from English to Norwegian. You MUST use this exact JSON structure: {\"exercise_type\": \"translation\", \"question\": \"Translate to Norwegian: ...\", \"answer\": \"...\", \"hint\": \"...\"}",
    
    # FILL IN THE BLANK
    "Generate a level 7 fill_in_blank exercise in Norwegian. ONE only sentence which must be very short (MAX 8 words). You MUST use this exact JSON structure: {\"exercise_type\": \"fill_in_blank\", \"sentence_with_blank\": \"... ___ ...\", \"answer\": \"...\", \"hint\": \"...\"}"
]

for prompt in test_prompts:
    print(f"\n--- PROMPT: {prompt} ---")
    
    response = client.chat.completions.create(
        model="local-model", # LM Studio ignores this and uses the loaded model
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4, # LOWERED to 0.1 for maximum strictness
        max_tokens=300
    )
    
    output = response.choices[0].message.content
    
    # 1. Remove any markdown backticks the model might have added
    output = output.replace("```json", "").replace("```", "").strip()

    # 2. Find the actual JSON object (from the first '{' to the last '}')
    start_idx = output.find('{')
    end_idx = output.rfind('}')
    
    if start_idx != -1 and end_idx != -1:
        clean_output = output[start_idx:end_idx+1]
    else:
        clean_output = output # Fallback if no brackets are found

    print("MODEL OUTPUT:")
    print(clean_output)
    
    try:
        parsed_json = json.loads(clean_output)
        print("✅ VALID JSON!")
        # You can now safely use parsed_json in your app!
    except json.JSONDecodeError:
        print("❌ INVALID JSON! The model failed the format test.")