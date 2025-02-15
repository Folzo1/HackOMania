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
import google.generativeai as genai
from google import genai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('GOOGLE_API_KEY')
client = genai.Client(api_key=API_KEY)

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
#edit this part
def process_instructions_with_gemini(raw_instructions, recipe_title):
    """
    Uses the Google Gemini API to refine recipe instructions.

    :param raw_instructions: The unstructured recipe instructions from the database.
    :param recipe_title: The title of the recipe for context.
    :return: A cleaned, structured, and numbered list of steps.
    """
    prompt = f"""
    You are a helpful cooking assistant in a food app. 
    Format these instructions for "{recipe_title}" into a clear, numbered step-by-step guide.
    Be detailed and easy to follow. Start directly with the numbered steps.
    Do not include any introductory text, disclaimers, or phrases like "Here's the recipe" or "Here are the steps".
    Just provide the numbered steps, formatted for mobile app display.
    DO NOT ever use Markdown formatting, make it in a human-readable format.

    Raw instructions:
    {raw_instructions}
    """

    try:
        # Request content generation using Google Gemini model
        response = client.models.generate_content(
            model="models/gemini-2.0-flash-lite-preview-02-05",  # Use the appropriate Gemini model
            contents=prompt,
        )

        # Get the cleaned response text
        response_text = response.text.strip()

        # Remove any common prefixes that the LLM might still add
        response_text = re.sub(r'^(Sure!|Here is|Here are|These are|Following are|Step-by-step guide:?)\s*', '', response_text, flags=re.IGNORECASE).strip()

        return response_text
    except Exception as e:
        return f"Error processing instructions with Gemini: {e}"

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
        return jsonify({"error": "Missing required field: 'images'. Please upload image files."}), 400

    session_id = request.form.get('session_id')
    if not session_id:
        return jsonify({"error": "Missing required field: 'session_id'. Please provide a session ID."}), 400

    images = request.files.getlist('images')
    if not images:
        return jsonify({"error": "No image files provided. Ensure you are uploading images."}), 400

    products = []
    errors = []

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
    required_fields = ['session_id']
    
    # Find missing fields
    missing_fields = [field for field in required_fields if field not in data or not data[field]]

    if missing_fields:
        return jsonify({
            "error": f"Missing required field(s): {', '.join(missing_fields)}. Please provide all necessary fields."
        }), 400

    session_id = data['session_id']
    products = get_session_products(session_id)

    if not products:
        return jsonify({"error": "No products found for this session. Please scan products first."}), 400

    recipe_conn = sqlite3.connect('backend/recipes.db')
    recipe_conn.row_factory = sqlite3.Row
    cursor = recipe_conn.cursor()

    try:
        cursor.execute('SELECT * FROM recipes')
        recipes = cursor.fetchall()

        matches = []
        for recipe in recipes:
            recipe_ingredients = []
            if 'Ingredients' in recipe.keys():
                ingredients_text = recipe['Ingredients']
                if ingredients_text:
                    recipe_ingredients = [ing.strip() for ing in ingredients_text.split(',')]

            matching_ingredients = sum(
                any(check_product_matches_ingredient(product, ingredient) for product in products)
                for ingredient in recipe_ingredients
            )

            match_percentage = (matching_ingredients / len(recipe_ingredients) * 100) if recipe_ingredients else 0

            if matching_ingredients > 0:
                matches.append({
                    'recipe_id': recipe['id'],
                    'title': recipe['Title'],
                    'instructions': recipe['Instructions'],
                    'matching_ingredients': matching_ingredients,
                    'total_ingredients': len(recipe_ingredients),
                    'match_percentage': round(match_percentage, 2),
                })

        matches = sorted(matches, key=lambda x: x['match_percentage'], reverse=True)[:2]

        for i in range(len(matches)):
            matches[i]['instructions'] = process_instructions_with_gemini(matches[i]['instructions'], matches[i]['title'])

        if not matches:
            return jsonify({"error": "No matching recipes found. Try scanning more relevant products."}), 404

        log_file = save_matches_to_file(session_id, matches)

        return jsonify({
            "matches": matches,
            "log_file": log_file
        })

    finally:
        recipe_conn.close()

if __name__ == "__main__":
    init_db()
    app.run(port=8000, debug=True)
