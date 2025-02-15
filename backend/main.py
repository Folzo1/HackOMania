from flask import Flask, request, jsonify
import cv2
from pyzbar.pyzbar import decode
import requests
import sqlite3
import re
import os
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
            ingredients TEXT,
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
        ingredients_text = product.get("ingredients_text", "")
            
        return {
            "product_name": product.get("product_name", "Unknown Product"),
            "category": product.get("categories", "Unknown Category"),
            "ingredients": ingredients_text,
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
        (barcode, product_name, category, ingredients, scan_date, session_id)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        product_info['barcode'],
        product_info['product_name'],
        product_info['category'],
        product_info['ingredients'],
        datetime.now(),
        session_id
    ))
    conn.commit()
    conn.close()

# Recipe matching functions
def extract_main_ingredient(ingredient_text):
    text = ingredient_text.lower()
    text = re.sub(r'^\d+\/?\d*\s*', '', text)
    text = re.sub(r'^\d+\-\d+\s*', '', text)
    
    # Common ingredients and measurements lists...
    measurements = {'tablespoon', 'teaspoon', 'cup', 'ounce', 'oz', 'pound', 'lb',
                   'gram', 'kg', 'ml', 'liter', 'pinch', 'dash'}
    
    descriptors = {'large', 'small', 'medium', 'fresh', 'dried', 'chopped', 'diced',
                  'sliced', 'minced', 'coarse', 'fine', 'finely', 'coarsely',
                  'ground', 'whole', 'freshly'}
    
    common_ingredients = {'salt', 'pepper', 'oil', 'water', 'butter', 'garlic', 'sugar',
                         'flour', 'vinegar', 'sauce', 'spice', 'herb', 'seasoning'}
    
    words = text.split(',')[0].split()
    words = [word for word in words if word not in measurements and word not in descriptors]
    
    main_ingredient = words[-1] if words else ''
    is_common = main_ingredient in common_ingredients
    
    return main_ingredient, is_common

def get_session_ingredients(session_id):
    conn = sqlite3.connect('backend/products.db')
    c = conn.cursor()
    c.execute('SELECT ingredients FROM scanned_products WHERE session_id = ?', (session_id,))
    ingredients = c.fetchall()
    conn.close()
    
    # Combine all ingredients into a single list
    all_ingredients = []
    for ing_text in ingredients:
        if ing_text[0]:  # if ingredients text is not empty
            all_ingredients.extend([i.strip() for i in ing_text[0].split(',')])
    return {ing: 1 for ing in all_ingredients if ing}

# API Endpoints
@app.route('/user_info', methods=['GET'])
def get_user_info():
    # Get the 'profile' and 'effort_level' parameters from the query string
    profile = request.args.get('profile')
    effort_level = request.args.get('effort_level')

    # Check if both parameters are provided
    if not profile or not effort_level:
        return jsonify({"error": "Both 'profile' and 'effort_level' parameters are required"}), 400
    
    # You can now perform any logic with these parameters (for example, saving to the database, processing, etc.)
    # For the sake of example, we just return them in the response
    return profile, effort_level

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
        
    ingredients = get_session_ingredients(session_id)
    
    # Connect to recipe database
    recipe_conn = sqlite3.connect('backend/recipes.db')
    recipe_conn.row_factory = sqlite3.Row
    cursor = recipe_conn.cursor()
    
    try:
        cursor.execute('SELECT * FROM recipes')
        recipes = cursor.fetchall()
        
        matches = []
        for recipe in recipes:
            # Compare ingredients and find matches
            # Add recipe processing logic here
            processed_instructions = process_instructions_with_qwen(recipe['Instructions'])
            
            matches.append({
                'recipe_id': recipe['id'],
                'title': recipe['Title'],
                'instructions': processed_instructions
            })
        
        return jsonify(matches)
        
    finally:
        recipe_conn.close()

def process_instructions_with_qwen(ingredients):
    profile = get_user_info()[0]
    effort_level = get_user_info()[1]
    try:
        prompt = f'''Here is a list of the ingredients I have with its respective quantities: {ingredients}
            I am a {profile} and want my effort level for preparing the food to be {effort_level}. 
            Help me create a delicious recipe based on the abovementioned parameters.
            DO NOT give any unnecessary replies (eg confirming my prompt). 
            STRICTLY stick to the ingredients from the ingredients list.
            Return the following, separated, in JSON format: Ingredients Used, Instructions.
        '''
        # Add your Qwen LLM implementation here
        processed_instructions = instructions  # Placeholder
        return processed_instructions
    except Exception as e:
        return f"Error processing instructions: {str(e)}"

if __name__ == "__main__":
    init_db()
    app.run(port=8000, debug=True)
