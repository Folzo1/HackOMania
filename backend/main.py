from flask import Flask, request, jsonify
import cv2
from pyzbar.pyzbar import decode
import requests
import sqlite3
import re
import os
import json
from datetime import datetime
from bs4 import BeautifulSoup

app = Flask(__name__)

# Database initialization
def init_db():
    # Create products database
    conn = sqlite3.connect('backend/products.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS scanned_products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            barcode TEXT,
            product_name TEXT,
            category TEXT,
            scan_date TIMESTAMP,
            session_id TEXT
        )
    ''')
    conn.commit()
    conn.close()
    
    # Ensure recipe database connection works
    recipe_conn = sqlite3.connect('backend/recipes.db')
    recipe_conn.row_factory = sqlite3.Row
    recipe_conn.close()
    
    # Create logs directory if it doesn't exist
    os.makedirs('backend/logs', exist_ok=True)

# Barcode scanning functions
def preprocess_image(image_path):
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Failed to load image")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
    return thresh

def scan_barcode(image_path):
    try:
        processed_image = preprocess_image(image_path)
        barcodes = decode(processed_image)
        
        if not barcodes:
            return None, "No barcode detected"
            
        for barcode in barcodes:
            barcode_data = barcode.data.decode("utf-8")
            return barcode_data, f"Barcode detected: {barcode_data}"
            
        return None, "No valid barcode found"
    except Exception as e:
        return None, f"Error processing barcode: {str(e)}"

# Product information functions
def get_product_info(barcode):
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if "product" not in data:
            return None
            
        product = data["product"]
            
        return {
            "product_name": product.get("product_name", "Unknown Product"),
            "category": product.get("categories", "Unknown Category"),
            "barcode": barcode
        }
    except Exception as e:
        print(f"Error fetching product info: {str(e)}")
        return None

def save_product_to_db(product_info, session_id):
    conn = sqlite3.connect('backend/products.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO scanned_products 
        (barcode, product_name, category, scan_date, session_id)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        product_info['barcode'],
        product_info['product_name'],
        product_info['category'],
        datetime.now(),
        session_id
    ))
    conn.commit()
    conn.close()

# Recipe matching functions
def get_session_products(session_id):
    conn = sqlite3.connect('backend/products.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT product_name, category FROM scanned_products WHERE session_id = ?', (session_id,))
    products = c.fetchall()
    conn.close()
    
    return [{"name": product['product_name'], "category": product['category']} for product in products]

# Add this set at the top of the recipe matching functions section
INGREDIENT_ADJECTIVES = {
    'fresh', 'dried', 'frozen', 'canned', 'organic', 'chopped', 'minced',
    'grated', 'sliced', 'ground', 'roasted', 'raw', 'cooked', 'smoked',
    'sweet', 'sour', 'spicy', 'boneless', 'skinless', 'whole', 'low-fat',
    'non-fat', 'extra-virgin', 'cold-pressed', 'pure', 'natural', 'artificial',
    'light', 'dark', 'powdered', 'crushed', 'peeled', 'seeded', 'diced',
    'shredded', 'cubed', 'marinated', 'pickled', 'aged', 'unsalted', 'salted',
    'sweetened', 'unsweetened', 'flavored', 'unflavored', 'premium', 'homemade',
    'store-bought', 'crispy', 'soft', 'hard', 'mild', 'hot', 'ripe', 'unripe',
    'bitter', 'creamy', 'crunchy', 'juicy', 'lean', 'fatty', 'thick', 'thin',
    'liquid', 'dry', 'moist', 'tender', 'tough', 'wild', 'cultivated', 'pasteurized',
    'unpasteurized', 'gluten-free', 'vegan', 'vegetarian', 'kosher', 'halal'
}

def check_product_matches_ingredient(product, ingredient):
    # Normalize and remove adjectives
    ingredient = ingredient.lower().strip()
    ingredient_words = re.findall(r'\b\w+\b', ingredient)
    base_ingredient = ' '.join([word for word in ingredient_words 
                              if word not in INGREDIENT_ADJECTIVES])
    
    if not base_ingredient:
        return False
    
    product_name = product["name"].lower()
    product_category = product["category"].lower() if product["category"] else ""

    # Check base matches
    if (base_ingredient in product_name or 
        product_name in base_ingredient or
        base_ingredient in product_category):
        return True
    
    # Check word components
    base_words = set(re.findall(r'\b\w+\b', base_ingredient))
    product_words = set(re.findall(r'\b\w+\b', f"{product_name} {product_category}"))
    
    # Require at least 3-letter matches to avoid short word false positives
    meaningful_matches = [word for word in base_words 
                        if word in product_words and len(word) > 2]
    
    return len(meaningful_matches) > 0

def process_instructions_with_qwen(raw_instructions, recipe_title):
    """
    Uses the locally running Qwen model via Ollama to refine recipe instructions.

    :param raw_instructions: The unstructured recipe instructions from the database.
    :param recipe_title: The title of the recipe for context.
    :return: A cleaned, structured, and numbered list of steps.
    """
    prompt = f"""
    You are a helpful cooking assistant in a food app. 
    Format these instructions for "{recipe_title}" into a clear, numbered step-by-step guide.
    Keep it concise and easy to follow. Start directly with the numbered steps.
    Do not include any introductory text, disclaimers, or phrases like "Here's the recipe" or "Here are the steps".
    Just provide the numbered steps, formatted for mobile app display.

    Raw instructions:
    {raw_instructions}
    """

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "qwen2.5", "prompt": prompt, "stream": False}  # Disable streaming
    )

    try:
        response_json = response.json()  # Convert response to JSON
        response_text = response_json.get("response", "Error processing instructions.")
        
        # Remove any common prefixes that the LLM might still add
        response_text = re.sub(r'^(Sure!|Here is|Here are|These are|Following are|Step-by-step guide:?)\s*', '', response_text, flags=re.IGNORECASE).strip()
        
        return response_text
    except requests.exceptions.JSONDecodeError as e:
        return f"JSON parsing error: {e}, Response content: {response.text}"

# Save matches to a file
def save_matches_to_file(session_id, matches):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"backend/logs/recipe_matches_{session_id}_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(matches, f, indent=2)
    
    return filename

# API Endpoints
@app.route('/scan', methods=['POST'])
def scan_and_process():
    if 'images' not in request.files:
        return jsonify({"error": "No image files provided"}), 400
        
    session_id = request.form.get('session_id')
    if not session_id:
        return jsonify({"error": "No session ID provided"}), 400
        
    images = request.files.getlist('images')
    products = []
    errors = []

    # Create temporary directory
    temp_dir = 'temp_images'
    os.makedirs(temp_dir, exist_ok=True)

    for image in images:
        if image.filename == '':
            errors.append({"file": "No file selected", "error": "Empty filename"})
            continue
            
        image_path = os.path.join(temp_dir, image.filename)
        image.save(image_path)
    
        try:
            barcode_data, message = scan_barcode(image_path)
            if not barcode_data:
                errors.append({"file": image.filename, "error": message})
                continue
                
            product_info = get_product_info(barcode_data)
            if not product_info:
                errors.append({"file": image.filename, "error": "Product not found in database"})
                continue
                
            save_product_to_db(product_info, session_id)
            products.append(product_info)
            
        except Exception as e:
            errors.append({"file": image.filename, "error": f"Error processing image: {str(e)}"})
            
        finally:
            if os.path.exists(image_path):
                os.remove(image_path)

    if not products and not errors:
        return jsonify({"error": "No valid products processed"}), 400
        
    return jsonify({
        "message": "Processed images",
        "products": products,
        "errors": errors
    })

@app.route('/generate_recipe', methods=['POST'])
def generate_recipe():
    data = request.get_json()
    session_id = data.get('session_id')
    
    if not session_id:
        return jsonify({"error": "No session ID provided"}), 400
        
    products = get_session_products(session_id)
    
    # Connect to recipe database
    recipe_conn = sqlite3.connect('backend/recipes.db')
    recipe_conn.row_factory = sqlite3.Row
    cursor = recipe_conn.cursor()
    
    try:
        cursor.execute('SELECT * FROM recipes')
        recipes = cursor.fetchall()
        
        # First pass: calculate matches and percentages without processing instructions
        matches = []
        for recipe in recipes:
            # Parse recipe ingredients
            recipe_ingredients = []
            if 'Ingredients' in recipe.keys():
                ingredients_text = recipe['Ingredients']
                if ingredients_text:
                    recipe_ingredients = [ing.strip() for ing in ingredients_text.split(',')]
            
            # Check if any product matches any ingredient
            matching_ingredients = 0
            for ingredient in recipe_ingredients:
                for product in products:
                    if check_product_matches_ingredient(product, ingredient):
                        matching_ingredients += 1
                        break  # Move to next ingredient once a match is found
            
            # Calculate match percentage
            match_percentage = 0
            if recipe_ingredients:
                match_percentage = (matching_ingredients / len(recipe_ingredients)) * 100

            #Add thumbnail image URL 
            def get_first_image_url(query):
                query = query.replace(" ", "+")
                bing_search_url = f"https://www.bing.com/images/search?q={query}+filterui:imagesize-large"
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
                response = requests.get(bing_search_url, headers=headers)
                soup = BeautifulSoup(response.content, 'html.parser')
                image_tags = soup.find_all('img', {'class': 'mimg'})
                for img in image_tags:
                    img_url = img.get('data-src') or img.get('src')
                    if img_url and img_url.startswith('http'):
                        return img_url
                return None

            query = recipe['Title']
            image_url = get_first_image_url(query)

            if image_url:
                print("First image URL:", image_url)
            else:
                print("No images found.")

            
            # Only include recipes with at least one matching ingredient
            if matching_ingredients > 0:
                matches.append({
                    'recipe_id': recipe['id'],
                    'title': recipe['Title'],
                    'instructions': recipe['Instructions'],  # Original unprocessed instructions
                    'matching_ingredients': matching_ingredients,
                    'total_ingredients': len(recipe_ingredients),
                    'match_percentage': round(match_percentage, 2),
                    'imageURL': image_url
                })
        
        # Sort matches by match percentage in descending order
        matches = sorted(matches, key=lambda x: x['match_percentage'], reverse=True)[:2]

        # Second pass: process instructions only for top 2 matches
        for i in range(min(2, len(matches))):
            matches[i]['instructions'] = process_instructions_with_qwen(
                matches[i]['instructions'], 
                matches[i]['title']
            )
        
        # Save matches to file
        log_file = save_matches_to_file(session_id, matches)
        
        print(f"Saved {len(matches)} matches to {log_file}")
        return jsonify({
            "matches": matches,
            "log_file": log_file
        })
        
    finally:
        recipe_conn.close()

if __name__ == "__main__":
    init_db()
    app.run(port=8000, debug=True)
