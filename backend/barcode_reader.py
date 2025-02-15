import cv2
from pyzbar.pyzbar import decode

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
        print(f"barcode data: {barcode_data} type: {barcode_type}")
        return barcode_data

barcode_number = scan_barcode("coke2.jpg")
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
        return f"Product: {product_name}, Category: {category}"
    else:
        return "Product is not found in database"


product_info = get_prod_info(scan_barcode("coke2.jpg"))
print(product_info)
