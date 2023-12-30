import sys
import ordinals_parser as ord

def main():
    print("Welcome to the Bitcoin Transaction to Inscription Converter.")
    print("This program extracts witness data from a Bitcoin transaction and saves the inscription to a file.")
    print("It supports almost any file types (images, videos, text, etc.) but does not support recursive inscriptions.")
    transaction_id = input("Please enter the transaction ID of the inscription you would like to save: ")

    try:
        witness_data = ord.get_witness_data_from_tx_id(transaction_id)
        mime_type, inscription = ord.find_envelope_and_inscription(witness_data)
        if inscription:
            output_file = "inscription"  # Base name for the output file
            extension = ord.mime_type_to_extension(mime_type)
            output_file_with_extension = f"{output_file}.{extension}"
            print(f"MIME Type: {mime_type}")
            ord.inscription_data_to_file(mime_type, inscription, output_file)
            print(f"Inscription saved to {output_file_with_extension}")
        else:
            print("No inscription found in the provided transaction ID.")
    except Exception as e:
        print(f"Could not retrieve transaction data.")

if __name__ == "__main__":
    main()