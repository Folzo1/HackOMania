import cv2
from pyzbar.pyzbar import decode
import requests

def preprocess_image(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
    return thresh

def scan_barcode(image_path):
    processed_image = preprocess_image(image_path)
    barcodes = decode(processed_image)
    
    if not barcodes:
        return "barcode not detected!"
        
    for barcode in barcodes:
        barcode_data = barcode.data.decode("utf-8")
        barcode_type = barcode.type
        print(f"Barcode data: {barcode_data} Type: {barcode_type}")
        return barcode_data

def get_prod_info(barcode):
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    response = requests.get(url)
    data = response.json()
    
    if "product" in data:
        product_name = data["product"].get("product_name", "Unknown Product")
        category = data["product"].get("categories", "Unknown Category")
        
        # Send the product info to main.py
        product_data = {
            "product_name": product_name,
            "category": category,
            "barcode": barcode
        }
        
        # Send POST request to main.py
        try:
            response = requests.post('http://localhost:5000/add_product', json=product_data)
            if response.status_code == 200:
                print("Product info successfully sent to main.py")
            else:
                print("Failed to send product info")
        except requests.exceptions.RequestException as e:
            print(f"Error sending request: {e}")
            
        return f"Product: {product_name}, Category: {category}"
    else:
        return "Product not found in database"

if __name__ == "__main__":
    barcode_number = scan_barcode("coke2.jpg")
    print("Scanned barcode: " + str(barcode_number))
    product_info = get_prod_info(barcode_number)
    print(product_info)