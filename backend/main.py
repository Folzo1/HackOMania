from flask import Flask, request, jsonify

app = Flask(__name__)

# Sample initial data in-memory store (only name and value)
data_store = [
    {"name": "item1", "value": "100"},
    {"name": "item2", "value": "200"},
    {"name": "item3", "value": "300"}
]

# Function to display data on startup
def display_data():
    print("Current Data Store:")
    for item in data_store:
        print(f"Name: {item['name']}, Value: {item['value']}")
    print("-" * 40)

# GET endpoint to retrieve all data (filtered by name if provided)
@app.route('/data', methods=['GET'])
def get_data():
    name = request.args.get('name')  # Get the name query parameter
    
    # If no name is provided, return all data
    if not name:
        return jsonify(data_store)
    
    # Filter the data by matching the name
    filtered_data = [item for item in data_store if name.lower() in item['name'].lower()]
    
    return jsonify(filtered_data)

'''
Create a detailed and personalised meal plan based on the following information: 

**User Profile:**
- Age: [User's age]
- Dietary preferences: [User's dietary preferences, e.g., vegetarian, vegan, omnivore, gluten-free, etc.]
- Allergies or food sensitivities: [List any allergies or sensitivities, if applicable]
- Other preferences: [List any other specific preferences such as low-carb, high-protein, quick meals, etc.]

**Available Ingredients:**
- Ingredient 1: [Ingredient Name] (Amount: [Amount available])
- Ingredient 2: [Ingredient Name] (Amount: [Amount available])
- Ingredient 3: [Ingredient Name] (Amount: [Amount available])
- [Add more ingredients as needed]

**Desired Portion Sizes:**
- Number of meals: [Number of meals the user wants to plan for, e.g., 7 days, 3 meals per day, etc.]
- Serving size per meal: [Amount of food per meal, e.g., 1 cup, 2 servings, etc.]

**Desired Effort Level:**
- Low: [Minimal prep time, few ingredients, quick cooking process]
- Medium: [Moderate prep and cooking time, a few steps]
- High: [Complex recipes with more ingredients and prep time]

The meal plan should cater to the user's specific preferences, available ingredients, desired portion sizes, and effort level. Make sure to:
- Provide a variety of meal options (breakfast, lunch, and dinner) with clear, step-by-step recipes.
- Suggest meal options that use available ingredients efficiently, and offer substitutions when needed if ingredients are insufficient.
- Tailor the recipes according to the desired effort level (low, medium, high).
- Ensure the plan is nutritionally balanced, considering the user's dietary restrictions and preferences.
- Ensure each recipe is clear, concise, and easy to follow.

End the response with a complete meal plan for the user, offering a variety of options and including the ingredients and cooking instructions for each meal.
'''

# Sample LLM response (meal plan)
llm_response = {
    "meal_plan": {
        "breakfast": {
            "name": "Scrambled Tofu with Veggies",
            "ingredients": ["Tofu", "Spinach", "Tomatoes", "Olive oil", "Garlic", "Salt", "Pepper"],
            "steps": [
                "Heat olive oil in a pan and sauté garlic until fragrant.",
                "Add chopped tomatoes and spinach, cook for 2 minutes.",
                "Add crumbled tofu, salt, and pepper, and cook for another 5 minutes until tofu is golden brown."
            ]
        },
        "lunch": {
            "name": "Quinoa Salad with Roasted Vegetables",
            "ingredients": ["Quinoa", "Carrots", "Zucchini", "Olive oil", "Lemon juice", "Salt", "Pepper"],
            "steps": [
                "Cook quinoa as per package instructions.",
                "Roast chopped carrots and zucchini with olive oil, salt, and pepper for 20 minutes at 180°C.",
                "Combine quinoa with roasted vegetables, drizzle with lemon juice, and serve."
            ]
        },
        "dinner": {
            "name": "Grilled Chicken with Sweet Potato and Broccoli",
            "ingredients": ["Chicken breast", "Sweet potato", "Broccoli", "Olive oil", "Salt", "Pepper"],
            "steps": [
                "Grill the chicken breast until cooked through (about 6 minutes per side).",
                "Roast sweet potato cubes with olive oil, salt, and pepper for 25 minutes at 200°C.",
                "Steam broccoli for 5-7 minutes, then serve with the grilled chicken and roasted sweet potato."
            ]
        }
    }
}

# Route to return the LLM response as a JSON
@app.route('/recipes', methods=['POST'])
def publish_recipes():
    return jsonify(llm_response), 200

if __name__ == '__main__':
    display_data()  # Display data when the server starts
    app.run(debug=True)

#change the port number 
