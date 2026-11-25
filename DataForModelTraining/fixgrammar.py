import json

with open('training_data1.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

cleaned_data = []

for item in data:
    # Only process translation exercises
    if item['input']['exercise_type'] == 'translation':
        word_pool = item['output'].get('word_pool', [])
        
        # Split full sentences into individual words
        new_pool = []
        for item_in_pool in word_pool:
            # Split by space and strip punctuation
            words = item_in_pool.split()
            for w in words:
                clean_w = w.strip('.,?!')
                if clean_w and clean_w not in new_pool:
                    new_pool.append(clean_w)
        
        item['output']['word_pool'] = new_pool
        
    cleaned_data.append(item)

with open('Fixed_Data.json', 'w', encoding='utf-8') as f:
    json.dump(cleaned_data, f, ensure_ascii=False, indent=4)

print(f"Fixed {len(cleaned_data)} records. Word pools are now single words.")