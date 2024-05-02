import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import fuzz
import re
from tqdm import tqdm

def find_pieces(food_item):
    # Convert the food item to lowercase for case-insensitive comparison
    food_item_lower = str(food_item).lower()

    # Check if any of the specific unit keywords are found in the food item string
    specific_units = ['pcs', 'pieces', 'piece']
    for unit_keyword in specific_units:
        if unit_keyword in food_item_lower:
            match = re.match(r".*?(\d*\.?\d+)\s*({})".format(unit_keyword), food_item_lower, re.IGNORECASE)
            if match:
                quantity = float(match.group(1))
                unit = match.group(2).lower()
                return quantity, unit

    return None, None 

def preprocess_food_item(food_item):
    pcs_quantity, pcs_unit = find_pieces(food_item)
    if pcs_quantity is None and pcs_unit is None:
        parts = str(food_item).lower().split()
        halfway = len(parts) // 2
        second_half = ' '.join(parts[halfway:])
        
        quantity = None
        unit = None
        
        match = re.match(r".*?(\d*\.?\d+)\s*(kg|kilogram|g|gram|ml|milliliter|L|liter|litre|lbs|pound|inch|pieces|pcs|oz|ounce)", second_half, re.IGNORECASE)

        if match:
            value = float(match.group(1))
            unit = match.group(2).lower()
            if unit in ['g', 'gram']:
                value /= 1000
                unit = 'kg'
            elif unit in ['lbs', 'pound']:
                value *= 0.453592
                unit = 'kg'
            elif unit in ['ml', 'milliliter']:
                value /= 1000
                unit = 'L'
            quantity = value
        else:
            if any(word in second_half.lower() for word in ['small', 'medium', 'large','full','half']):
                unit = [word for word in ['small', 'medium', 'large','full','half'] if word in second_half.lower()][0]
                quantity = 1
            else:
                match = re.match(r".*?(\d*\.?\d+:\d*\.?\d+)\s*$", second_half, re.IGNORECASE)
                if match:
                    unit = match.group(1)
                    quantity = 1

        return quantity, unit
    else:
        return pcs_quantity,pcs_unit

def set_and_combos(food_item):
    # Convert the food item to lowercase for case-insensitive comparison
    food_item_lower = str(food_item).lower()

    # List of phrases to check for
    phrases_to_check = ['set menu', 'set meal', 'combo menu', 'combo meal','combo','set-menu','set-meal','combo-meal','combo-menu','set - menu','set - meal',' combo - meal','combo - menu']

    # Regular expression pattern to match the phrase followed by an optional hyphen and space before the number
    pattern = r'({})(?:\s*-\s*)?(\d+)'.format('|'.join(map(re.escape, phrases_to_check)))

    # Search for the pattern in the food item
    match = re.search(pattern, food_item_lower)

    if match:
        phrase = match.group(1)
        number = match.group(2)
        # print("combo 1:", phrase, "number:", number)
        return phrase, number
    
    # Return None for both values if no combo menu is found
    return None, None

def compare_products(product1, product2):
    quantity1, unit1 = preprocess_food_item(product1)
    quantity2, unit2 = preprocess_food_item(product2)

    if (unit1 is None and quantity1 is None) and (unit2 is None and quantity2 is None):
        similarity_score = fuzz.ratio(str(product1).lower(), str(product2).lower())
        return similarity_score
    else:
        if (unit1 == '1:1' or unit2 == '1:1') or (unit1 is not None and unit2 is not None):
            if unit1 and unit2:
                if unit1.lower() == unit2.lower():
                    if quantity1 and quantity2:
                        if round(quantity1, 2) == round(quantity2, 2):
                            product_clean_1 = re.sub(r"(\d+(\.\d+)?)\s*(kg|kilogram|gram|ml|milliliter|liter|litre|lbs|pound|inch|oz|ounce|pcs|full|half|small|medium|large)?", "", product1.lower()).strip()
                            product_clean_2 = re.sub(r"(\d+(\.\d+)?)\s*(kg|kilogram|gram|ml|milliliter|liter|litre|lbs|pound|inch|oz|ounce|pcs|full|half|small|medium|large)?", "", product2.lower()).strip()
                            
                            product_name1 = re.sub(r"\b(small|medium|large|full|half)\b", "", product_clean_1, flags=re.IGNORECASE).strip()
                            product_name2 = re.sub(r"\b(small|medium|large|full|half)\b", "", product_clean_2, flags=re.IGNORECASE).strip()
                            
                            similarity_score = fuzz.ratio(product_name1.lower(), product_name2.lower())
                            return similarity_score
                        else:
                            return 0 
                    else:
                        product_clean_1 = re.sub(r"(\d+(\.\d+)?)\s*(kg|kilogram|gram|ml|milliliter|liter|litre|lbs|pound|inch|oz|ounce|full|half|small|medium|large)?", "", product1.lower()).strip()
                        product_clean_2 = re.sub(r"(\d+(\.\d+)?)\s*(kg|kilogram|gram|ml|milliliter|liter|litre|lbs|pound|inch|oz|ounce|full|half|small|medium|large)?", "", product2.lower()).strip()
                        product_name1 = re.sub(r"\b(small|medium|large|full|half)\b", "", product_clean_1, flags=re.IGNORECASE).strip()
                        product_name2 = re.sub(r"\b(small|medium|large|full|half)\b", "", product_clean_2, flags=re.IGNORECASE).strip()
                        similarity_score = fuzz.ratio(product_name1.lower(), product_name2.lower())
                        return similarity_score
                else:
                    return 0 
            else:
                similarity_score = fuzz.ratio(product1.lower(), product2.lower())
                return similarity_score
        else:
            return 0

def food_item_matcher(food_item_1, food_item_2):
    combo_menu_1, combo_number_1 = set_and_combos(food_item_1)
    combo_menu_2, combo_number_2 = set_and_combos(food_item_2)

    if combo_menu_1 is not None and combo_menu_2 is not None and combo_number_1 is not None and combo_number_2 is not None:
        if combo_menu_1.lower() == combo_menu_2.lower() and combo_number_1 == combo_number_2:
            similarity_score = fuzz.ratio(food_item_1.lower(), food_item_2.lower())
            return similarity_score
        elif combo_menu_1.lower() == combo_menu_2.lower() and combo_number_1!= combo_number_2:
            return 0
        else:
            return 0
    elif (combo_menu_1 is None and combo_number_1 is None) and (combo_menu_2 is not None and combo_number_2 is not None):
        return 0
    elif (combo_menu_1 is not None and combo_number_1 is not None) and (combo_menu_2 is None and combo_number_2 is None):
        return 0
    else:
        compare = compare_products(food_item_1, food_item_2)
        return compare

def preprocess_text(text):
    if isinstance(text, str) and text.strip():
        text = text.lower()
        text = ''.join(e for e in text if e.isalnum() or e.isspace())
        return text
    else:
        return "" 

def calculate_similarity(description1, description2, threshold=0.7):
    preprocessed_description1 = preprocess_text(description1)
    preprocessed_description2 = preprocess_text(description2)

    if not preprocessed_description1 or not preprocessed_description2:
        return False, 0
    
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform([preprocessed_description1, preprocessed_description2])

    cosine_sim_matrix = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])

    if cosine_sim_matrix[0, 0] > threshold:
        return True, cosine_sim_matrix[0, 0]
    else:
        return False, cosine_sim_matrix[0, 0]

def compare_descriptions(description1, description2):
    preprocessed_description1 = preprocess_text(description1)
    preprocessed_description2 = preprocess_text(description2)

    if len(preprocessed_description1) < 3 or len(preprocessed_description2) < 3:
        return False, 0
    
    similarity_score = calculate_similarity(preprocessed_description1, preprocessed_description2)
    return similarity_score

print("Loading comp1.csv...")
try:
    comp1_df = pd.read_csv('comp1.csv')
    print("comp1.csv loaded.")
except FileNotFoundError:
    print("Error: comp1.csv not found.")
    exit()
print("Loading comp1.csv...")
try:
    comp1_df = pd.read_csv('comp1.csv')
    print("comp1.csv loaded.")
except FileNotFoundError:
    print("Error: comp1.csv not found.")
    exit()

print("Loading comp21.csv...")
try:
    comp2_df = pd.read_csv('comp21.csv', dtype=str)
    print("comp21.csv loaded.")
except FileNotFoundError:
    print("Error: comp21.csv not found.")
    exit()

result_data = []

print("Starting comparison...")
try:
    for index, row in tqdm(comp1_df.iterrows(), total=len(comp1_df)):
        matching_vendor = comp2_df[comp2_df['vendor_id'] == row['vendor_code']]
        
        if not matching_vendor.empty:
            for _, matching_row in matching_vendor.iterrows():
                try:
                    similarity_score = compare_descriptions(row['product_description'], matching_row['description'])
                    fuzzy_ratio = food_item_matcher(row['product_title'], matching_row['item_name'])
                    result_data.append({
                        'vendor_code': str(row['vendor_code']),
                        'vendor_name': str(row['vendor_name']),
                        'product_title': str(row['product_title']),
                        'product_description': str(row['product_description']),
                        'product_variation_id': str(row['product_variation_id']),
                        'product_variation_price_local': row['product_variation_price_local'],
                        'vendor_id': str(matching_row['vendor_id']),
                        'item_name': str(matching_row['item_name']),
                        'description': str(matching_row['description']),
                        'price': matching_row['price'],
                        'description_score': similarity_score[1] if similarity_score[0] else 0,
                        'title_score': fuzzy_ratio
    
                    })
                except Exception as e:
                    print(f"Error processing row: {e}")
except Exception as e:
    print(f"Error during comparison loop: {e}")

result_df = pd.DataFrame(result_data)

result_df_filtered = result_df[(result_df['description_score'] >= 0.7) & (result_df['title_score'] >= 70)]

result_df_filtered.to_csv('price_comparison_result_filtered.csv', index=False)

print("Filtered result saved as price_comparison_result_filtered.csv.")
