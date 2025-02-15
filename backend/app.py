from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

pantry = []

@app.route('/scan', methods=['POST'])
def handle_scan():
    barcode = request.json.get('barcode')
    
    # Mock barcode lookup
    ingredients = {
        "123456": "Flour",
        "789012": "Eggs",
        "345678": "Sugar"
    }
    
    ingredient = ingredients.get(barcode, "Unknown Item")
    pantry.append(ingredient)
    
    return jsonify({
        "message": f"Added {ingredient} to pantry",
        "pantry": pantry
    })

@app.route('/generate-recipe', methods=['POST'])
def generate_recipe():
    ingredients = request.json.get('ingredients', [])
    
    # Mock recipe generation
    recipe = {
        "name": "Custom Recipe",
        "ingredients": ingredients,
        "instructions": "1. Mix all ingredients\n2. Bake at 350°F for 30 minutes"
    }
    
    return jsonify(recipe)

@app.route('/')
def health_check():
    return "Recipe Generator API Running"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)