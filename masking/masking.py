import os
import csv
import random
import string
import regex as re


def generate_uid():
    """Tạo một UID ngẫu nhiên gồm 8 chữ số."""
    return ''.join(random.choices(string.digits, k=8))

class CSVLoader:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.csv_contents = None

    def load_csv_files(self):
        """Load tất cả file CSV từ thư mục và lưu trữ nội dung."""
        if self.csv_contents is not None:
            return {"tool": "csv_placeholder_mask", "success": True, "csv_contents": self.csv_contents}

        self.csv_contents = {}
        try:
            for filename in os.listdir(self.folder_path):
                if filename.endswith('.csv'):
                    file_path = os.path.join(self.folder_path, filename)
                    place_holder = filename.split(".")[0]
                    with open(file_path, mode='r', encoding='utf-8') as file:
                        csv_reader = csv.reader(file)
                        for row in csv_reader:
                            for item in row:
                                self.csv_contents[item.strip()] = place_holder
            return {"tool": "csv_placeholder_mask", "success": True, "csv_contents": self.csv_contents}
        except Exception as e:
            return {"tool": "csv_placeholder_mask", "success": False, "error": str(e)}


class MaskingRule:
    def __init__(self):
        self.tenant = CSVLoader("./masking/black_list/tenant").load_csv_files()["csv_contents"]
        self.blacklist = CSVLoader("./masking/black_list/ignore").load_csv_files()["csv_contents"]


    def mask_text(self, text, placeholder_map = {}):
        masked_text, mask_map_tenant = self.mask_black_list(text, self.tenant, ignore=False, placeholder_map = placeholder_map )
        masked_text, mask_map_blacklist = self.mask_black_list(masked_text, self.blacklist, placeholder_map = placeholder_map)
        mask_map = {**mask_map_tenant, **mask_map_blacklist}
        return masked_text, mask_map

    def unmask_text(self, masked_text, mask_map):
        # Iterate over each key-value pair in mask_map
        for key, value in mask_map.items():
            # Use re.sub to replace occurrences of the key with the value, ignoring case
            masked_text = re.sub(re.escape(key), value, masked_text, flags=re.IGNORECASE)
        
        return masked_text
    
    def mask_black_list(self, text, replacement_map, ignore = True, placeholder_map = {}):
        placeholder_map = placeholder_map
        random_seed = generate_uid()
        def replace_with_placeholder_ignore(match):
            original_word = match.group(0)
            placeholder = replacement_map[original_word.lower()]
            if original_word not in placeholder_map.values():
                unique_placeholder = f"{placeholder}_masking_{abs(hash(original_word+random_seed))}"
                placeholder_map[unique_placeholder] = original_word
            else:
                found_keys = [key for key, value in placeholder_map.items() if value == original_word]
                unique_placeholder = found_keys[0]
            return unique_placeholder
        
        def replace_with_placeholder(match):
            original_word = match.group(0)
            placeholder = replacement_map[original_word]
            if original_word not in placeholder_map.values():
                unique_placeholder = f"{placeholder}_masking_{abs(hash(original_word+random_seed))}"
                placeholder_map[unique_placeholder] = original_word
            else:
                found_keys = [key for key, value in placeholder_map.items() if value == original_word]
                unique_placeholder = found_keys[0]
            return unique_placeholder

        # Prepare the regex pattern for all words to be replaced
        pattern = r'\b(?:' + '|'.join(re.escape(word) for word in replacement_map.keys()) + r')\b'
        # Replace each match with a uniquely generated placeholder
        if ignore:
            replacement_map = {key.lower(): value for key, value in replacement_map.items()}
            text = re.sub(pattern, replace_with_placeholder_ignore, text, flags=re.IGNORECASE)
        else:
            text = re.sub(pattern, replace_with_placeholder, text)

        return text, placeholder_map
        
# MaskingRule = MaskingRule()
# masked_text, mask_map = MaskingRule.mask_text(text = 'vpqh vpqh vpqh {"Name": "văn Phòng quốc hội", "Văn Phòng Quốc Hội", "category":"alert","tenant":"VPQH","query":"severity != \"Low\" AND tenant = \"vpqh\" AND created >= 1746032400000 AND created <= 1746896399000","count_only":false}')
# print(masked_text)
# print(mask_map)
# masked_text, mask_map = MaskingRule.mask_text(text = 'vpqh vpqh vpqh {"Name": "văn Phòng quốc hội", "Văn Phòng Quốc Hội", "category":"alert","tenant":"VPQH","query":"severity != \"Low\" AND tenant = \"vpqh\" AND created >= 1746032400000 AND created <= 1746896399000","count_only":false}', placeholder_map= mask_map)
# print(masked_text)
# print(mask_map)
# unmask_text = MaskingRule.unmask_text(masked_text, mask_map)
# print(unmask_text)