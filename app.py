import barcode
from barcode.writer import ImageWriter
import csv
import os
import re

def sanitize_filename(name):
    """
    Removes characters that are not allowed in filenames.
    """
    return re.sub(r'[\\/*?:"<>|]', "", name)

def generate_ean13_barcodes(csv_path, output_dir):
    """
    Reads a CSV file and generates EAN-13 barcodes for each valid row.

    Args:
        csv_path (str): The path to the input CSV file.
        output_dir (str): The directory where barcode images will be saved.
    """
    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")

    # Get the EAN13 barcode implementation
    EAN13 = barcode.get_barcode_class('ean13')

    print(f"Reading data from {csv_path}...")

    try:
        with open(csv_path, mode='r', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            # Skip the header row
            header = next(reader)
            print(f"CSV Header: {header}")

            for i, row in enumerate(reader, 1):
                # Ensure the row has the expected number of columns
                if len(row) != 2:
                    print(f"Skipping malformed row {i}: Expected 2 columns, but got {len(row)}. Content: {row}")
                    continue

                product_name, barcode_data = row
                
                # --- Data Validation ---
                # Check if barcode_data is a 12-digit string
                if not (barcode_data.isdigit() and len(barcode_data) == 12):
                    print(f"Skipping row {i} ('{product_name}'): Barcode data '{barcode_data}' is not a 12-digit number.")
                    continue

                try:
                    # Sanitize the product name to create a valid filename
                    safe_filename = sanitize_filename(product_name)
                    if not safe_filename.strip():
                        safe_filename = f"unnamed_product_{i}"

                    # The library will calculate the 13th checksum digit automatically.
                    # We specify the format as PNG. This requires the 'Pillow' library to be installed.
                    ean_barcode = EAN13(barcode_data, writer=ImageWriter(format='PNG'))

                    # Define the path for the output file. The writer will add the .png extension.
                    filepath = os.path.join(output_dir, safe_filename)

                    # Save the barcode image in PNG format.
                    # Add options to customize the output, like text visibility.
                    options = {
                        'module_width': 0.2, 
                        'module_height': 15.0, 
                        'font_size': 10,
                        'text_distance': 5.0,
                        'quiet_zone': 6.5
                    }
                    print(f"Generating PNG barcode for '{product_name}'...")
                    ean_barcode.write(filepath, options)

                except Exception as e:
                    print(f"Could not generate barcode for '{product_name}'. Error: {e}")

    except FileNotFoundError:
        print(f"Error: The file '{csv_path}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    print("\nBarcode generation process finished.")


if __name__ == "__main__":
    CSV_FILE = 'products.csv'
    OUTPUT_FOLDER = 'barcodes'
    generate_ean13_barcodes(CSV_FILE, OUTPUT_FOLDER)
