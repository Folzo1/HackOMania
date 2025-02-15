import cv2
from pyzbar.pyzbar import decode

def preprocess_image(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
    _, thresh = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)  # Apply thresholding
    return thresh

def scan_barcode(image_path):
    processed_image = preprocess_image(image_path)
    barcodes = decode(processed_image)

    if not barcodes:
        return "barcode not detected!"
    
    for barcode in barcodes:
        barcode_data = barcode.data.decode("utf-8")
        barcode_type = barcode.type
        print(f"barcode data: {barcode_data} type: {barcode_type}")
        return barcode_data

barcode_number = scan_barcode("crysanthemum.jpg") #INPUT
print("scanned barcode: "+str(barcode_number))


### API

import requests

def get_prod_info(barcode):
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    response = requests.get(url)
    data = response.json()

    if "product" in data:
        product_name = data["product"].get("product_name", "unknown Product")
        category = data["product"].get("categories", "Unknown Category")
        return [product_name, category]
    else:
        return "Product is not found in database"


product_info = get_prod_info(scan_barcode("coke1.jpg")) #INPUT
print(product_info)

######################################################################################################################################
######################################################################################################################################

### Category sorter
import nltk

nltk.download("wordnet")
nltk.download('omw-1.4')

from nltk.corpus import wordnet as wn

#food_root = wn.synsets("Food")[0]

root = ""

def check_synset_exists(category, pos='n'):
    try:
        synset = wn.synset(f'{category}.{pos}.01')
        return synset
    except:
        return None

def is_food_related(word, root):
    """Check if a word belongs under any part of the food hierarchy (including fruits, beverages, etc.)."""
    food_root = wn.synset("food.n.01")  # The food category in WordNet
    fruit_root = wn.synset("fruit.n.01")  # The fruit category in WordNet
    beverage_root = wn.synset("beverage.n.01")  # The beverage category in WordNet
    dairy_root = wn.synset("dairy_product.n.01")  # Dairy product category
    meat_root = wn.synset("meat.n.01")  # Meat category
    vegetable_root = wn.synset("vegetable.n.01")  # Vegetable category
    cereal_root = wn.synset("cereal.n.01")  # Cereal category
    specific_root = wn.synset(root+".n.01")
    # Get all synsets related to the word
    synsets = wn.synsets(word, pos=wn.NOUN)
    
    # Check if any synset belongs to any of the food-related categories
    for syn in synsets:
        if food_root in syn.hypernym_paths()[0] or \
           fruit_root in syn.hypernym_paths()[0] or \
           beverage_root in syn.hypernym_paths()[0] or \
           dairy_root in syn.hypernym_paths()[0] or \
           meat_root in syn.hypernym_paths()[0] or \
           vegetable_root in syn.hypernym_paths()[0] or \
           cereal_root in syn.hypernym_paths()[0]:
            return True
    return False

def get_max_depth(word, root):
    spec_root = wn.synset(root+".n.01")

    synsets = wn.synsets(word, pos=wn.NOUN)

    max_depth = 0
    for syn in synsets:
        for path in syn.hypernym_paths():
            if spec_root in path:
                max_depth = max(max_depth, len(path))
    return max_depth
    

def get_most_spec_food_cat(categories, root):
    food_cat = [cat for cat in categories if is_food_related(cat, root)]
    print(food_cat)
    if not food_cat:
        return None
    
    max_depth_cat = max(food_cat, key=lambda cat: get_max_depth(cat, root))
    return max_depth_cat
#from nltk.corpus import wordnet as wn

# Get all words in WordNet

prod = "Beverage, Carbonated drinks, Sodas, Colas"
ex = prod.split(", ")
#print(ex)
#print(wn.synset())




### DRIVER CODE

name = product_info[0]
cat = product_info[1]
#print("cat: "+cat)
ex = cat.split(", ")
#ex = ["fruit", "apple"]
#ex = ["Dairy", "Fermented foods", "cheeses"]
#ex = ["Breakfasts", "Spreads", "Chocolate spreads", "cocoa"]
#ex = ["Plant-based foods and beverages", "Snacks", "Crisps", "chips"]
#ex = ["Dairies", "Milks", "Fresh Milks", "Pasteurised Milks"]
root = ex[0].lower()
print(check_synset_exists(root))
most_specific = ""
final_res = [name]
s = check_synset_exists(root)
if s:
    most_specific = get_most_spec_food_cat(ex, root)
    print("most_specific: "+most_specific)
else:
    root = "food"
    most_specific = get_most_spec_food_cat(ex, root)
    print("most_specific: "+most_specific)

final_res.append(most_specific)
print(final_res)
