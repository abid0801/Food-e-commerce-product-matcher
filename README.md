# Product matcher for food e-commerce

This Python script is designed for comparing product descriptions and titles between two CSV files (`comp1.csv` and `comp21.csv`) and generating a filtered result based on certain criteria. It primarily utilizes pandas for data manipulation, scikit-learn for text vectorization and similarity calculation, fuzzywuzzy for fuzzy string matching, and tqdm for progress visualization.

## Prerequisites

Ensure you have the following dependencies installed:
- pandas
- scikit-learn
- fuzzywuzzy
- tqdm

You can install them using pip:

```bash
pip install pandas scikit-learn fuzzywuzzy tqdm
```

## Usage

1. Ensure `comp1.csv` and `comp21.csv` are present in the same directory as the script.
2. Run the script. It will load `comp1.csv` and `comp21.csv` into pandas dataframes for comparison.
3. The script iterates over each row in `comp1.csv`, matches corresponding rows in `comp21.csv` based on vendor code, and compares product descriptions and titles.
4. It then calculates similarity scores for descriptions and titles, filters the results based on certain thresholds (0.7 for description similarity and 70 for title similarity), and saves the filtered result in a new CSV file named `price_comparison_result_filtered.csv`.

## Functions

### `find_pieces(food_item)`
- Extracts quantity and unit from a food item string.

### `preprocess_food_item(food_item)`
- Preprocesses a food item string to extract quantity and unit.

### `set_and_combos(food_item)`
- Searches for set menu or combo menu phrases in a food item string.

### `compare_products(product1, product2)`
- Compares two food products based on their names, quantities, and units.

### `food_item_matcher(food_item_1, food_item_2)`
- Matches two food items based on whether they are part of a set or combo menu, or based on their names, quantities, and units.

### `preprocess_text(text)`
- Preprocesses text data by converting it to lowercase and removing non-alphanumeric characters.

### `calculate_similarity(description1, description2, threshold=0.7)`
- Calculates the cosine similarity between two preprocessed text descriptions.

### `compare_descriptions(description1, description2)`
- Compares two text descriptions based on cosine similarity.

## Output

The filtered result contains the following columns:
- `vendor_code`: Vendor code from `comp1.csv`.
- `vendor_name`: Vendor name from `comp1.csv`.
- `product_title`: Product title from `comp1.csv`.
- `product_description`: Product description from `comp1.csv`.
- `product_variation_id`: Product variation ID from `comp1.csv`.
- `product_variation_price_local`: Product variation price from `comp1.csv`.
- `vendor_id`: Vendor ID from `comp21.csv`.
- `item_name`: Item name from `comp21.csv`.
- `description`: Description from `comp21.csv`.
- `price`: Price from `comp21.csv`.
- `description_score`: Similarity score between descriptions.
- `title_score`: Fuzzy ratio score between product titles.

The filtered result is saved as `price_comparison_result_filtered.csv`.

## Error Handling

The script handles file loading errors and exceptions during the comparison loop by printing error messages.

## Note

Ensure the CSV files have the necessary columns (`vendor_code`, `vendor_name`, `product_description`, etc.) for proper execution.
