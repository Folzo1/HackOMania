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


#SAMPLE DATA

#ingredients map with key as ingredient and value as quantity (for weight, assume units)
ingredients = {'chicken': 500, 'broccoli': 3, 'milk': 500, 'egg': 10, 'lettuce': 100, 'banana': 5}
profile = 'busy entrepreneur'
effort = 'low' #low, mid, high
prompt = f'''Here is a list of the ingredients I have with its respective quantities: {ingredients}
            I am a {profile} and want my effort level for preparing the food to be {effort}. 
            Help me create a delicious recipe based on the abovementioned parameters.
            DO NOT give any unnecessary replies (eg confirming my prompt). 
            STRICTLY stick to the ingredients from the ingredients list.
            Return the following, separated, in JSON format: Ingredients Used, Instructions.
        '''

llm_response = '''json
{
  "Ingredients Used": ["chicken", "broccoli", "milk", "egg"],
  "Instructions": [
    "Slice the chicken into bite-sized pieces.",
    "Boil a large pot of water and add the chicken pieces. Cook for about 7 to 8 minutes or until fully cooked.",
    "Wash and steam the broccoli florets for about 4-5 minutes until tender but still crisp.",
    "In a saucepan, heat some water and add the milk. Beat the eggs in a bowl and slowly pour them into the milk while stirring constantly to avoid curdling. Add salt and pepper to taste. Simmer for about 5 minutes until the sauce thickens.",
    "Combine the cooked chicken pieces, steamed broccoli, and simmered egg milk sauce in a serving bowl.",
    "Mix everything together gently to ensure the flavors blend well."
  ]
}
'''

# Route to return the LLM response as a JSON
@app.route('/recipes', methods=['POST'])
def publish_recipes():
    return jsonify(llm_response), 200

if __name__ == '__main__':
    display_data()  # Display data when the server starts
    app.run(debug=True)

#change the port number 
