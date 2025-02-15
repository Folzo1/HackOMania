from flask import Flask, request, jsonify
import cv2
from pyzbar.pyzbar import decode
import requests
import sqlite3
import re
import os
import json
from datetime import datetime

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

def check_product_matches_ingredient(product, ingredient):
    # Normalize strings for comparison
    product_name = product["name"].lower()
    product_category = product["category"].lower() if product["category"] else ""
    ingredient = ingredient.lower().strip()
    # Basic exact match
    if ingredient in product_name:
        return True
    
    # Check if product name or category contains the ingredient
    words = re.findall(r'\b\w+\b', product_name)
    for word in words:
        if word in ingredient.split(" "):
            return True
    
    if product_category:
        category_words = re.findall(r'\b\w+\b', product_category)
        for word in category_words:
            if word in ingredient:
                return True
    
    return False

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
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400
        
    session_id = request.form.get('session_id')
    if not session_id:
        return jsonify({"error": "No session ID provided"}), 400
        
    image = request.files['image']
    image_path = "temp_image.jpg"
    image.save(image_path)
    
    try:
        barcode_data, message = scan_barcode(image_path)
        if not barcode_data:
            return jsonify({"error": message}), 400
            
        product_info = get_product_info(barcode_data)
        if not product_info:
            return jsonify({"error": "Product not found in database"}), 404
            
        save_product_to_db(product_info, session_id)
        
        return jsonify({
            "message": "Product scanned and saved successfully",
            "product_info": product_info
        })
        
    finally:
        if os.path.exists(image_path):
            os.remove(image_path)

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
            
            # Only include recipes with at least one matching ingredient
            if matching_ingredients > 0:
                matches.append({
                    'recipe_id': recipe['id'],
                    'title': recipe['Title'],
                    'instructions': recipe['Instructions'],  # Original unprocessed instructions
                    'matching_ingredients': matching_ingredients,
                    'total_ingredients': len(recipe_ingredients),
                    'match_percentage': round(match_percentage, 2)
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