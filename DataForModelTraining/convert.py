import json

# 1. Load your current data
with open('training_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

formatted_data = []

# 2. Loop through and convert to ChatML format
for item in data:
    # We create a prompt that tells the model what to do
    user_prompt = f"Generate a level {item['input']['level']} {item['input']['language']} exercise of type {item['input']['exercise_type']}. Direction: {item['input'].get('direction', 'N/A')}."
    
    # We convert the output dictionary into a JSON string for the assistant to learn to generate
    assistant_response = json.dumps(item['output'], ensure_ascii=False)

    formatted_data.append({
        "messages": [
            {"role": "user", "content": user_prompt},
            {"role": "assistant", "content": assistant_response}
        ]
    })

# 3. Save it as a JSONL file (JSON Lines format)
with open('train_data.jsonl', 'w', encoding='utf-8') as f:
    for entry in formatted_data:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')

print("Conversion complete! Saved as train_data.jsonl")


# import json

# # Load your messy data
# with open('CompleteDataSet.json', 'r', encoding='utf-8') as f:
#     data = json.load(f)

# cleaned_data = []
# seen_exercises = set()

# for item in data:
#     # Create a unique "fingerprint" for the exercise to check for duplicates
#     exercise_str = json.dumps(item['output'], sort_keys=True)
    
#     if exercise_str in seen_exercises:
#         continue # Skip it, we already have this exact exercise
        
#     # If it's a translation, clean the word_pool
#     if item['input']['exercise_type'] == 'translation':
#         # Only keep words in the word_pool that don't have spaces
#         cleaned_pool = [word for word in item['output'].get('word_pool', []) if ' ' not in word.strip()]
#         item['output']['word_pool'] = cleaned_pool
        
#         # If cleaning the pool removed too many words, skip this sample entirely
#         if len(cleaned_pool) < 3:
#             continue

#     seen_exercises.add(exercise_str)
#     cleaned_data.append(item)

# # Save the clean data
# with open('CleanDataSet.json', 'w', encoding='utf-8') as f:
#     json.dump(cleaned_data, f, ensure_ascii=False, indent=4)

# print(f"Original size: {len(data)} samples.")
# print(f"Cleaned size: {len(cleaned_data)} samples.")