import os
import json

# Define source and target folders
txt_folder = "./prompts/roles_txt"
json_folder = "./prompts/roles"
os.makedirs(json_folder, exist_ok=True)

# Loop through all .txt files in the txt folder
for filename in os.listdir(txt_folder):
    if filename.endswith('.txt'):
        txt_path = os.path.join(txt_folder, filename)
        json_path = os.path.join(json_folder, filename.replace('.txt', '.json'))

        with open(txt_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()

        data = {
            "prompt": content,
            "max_replans": 3
        }

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

print("✅ Conversion complete.")