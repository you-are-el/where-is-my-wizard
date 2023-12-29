import requests
import base64

def get_full_transaction_from_tx_id(tx_id):
    url = f'https://mempool.space/api/tx/{tx_id}'
    response = requests.get(url)
    return response.json()

def get_witness_data_from_tx_id(tx_id):
    url = f'https://mempool.space/api/tx/{tx_id}'
    response = requests.get(url)
    tx_witness = ''.join(response.json()['vin'][0]['witness'])
    return tx_witness

def hex_to_bytes(hex_string):
    return bytes.fromhex(hex_string)

def bytes_to_ascii(byte_data):
    return byte_data.decode('ascii')

def mime_type_to_extension(mime_type):
    # Mapping common MIME types to file extensions
    mapping = {
        'image/png': 'png',
        'image/jpeg': 'jpg',
        'image/webp': 'webp',
        'image/gif': 'gif',
        'text/plain': 'txt',
        'text/plain;charset=utf-8': 'txt',
        'text/html;charset=utf-8': 'html',
        'text/x-python': 'py',
        'video/mp4': 'mp4',
        'audio/mpeg': 'mpeg',
        'model/gltf-binary': 'glb',
        'image/svg+xml': 'svg',
        # Add more mappings as needed
    }
    return mapping.get(mime_type, 'bin')  # Default to 'bin' for binary data

def find_envelope_and_inscription(hex_string):
    # Define the envelope format and opcodes in hex
    OP_FALSE = '00'
    OP_IF = '63'
    ORD = '036f7264'
    OP_1 = '0101'
    OP_0 = '00'
    OP_PUSHDATA1 = '4c'
    OP_PUSHDATA2 = '4d'
    OP_PUSHDATA4 = '4e'
    OP_ENDIF = '68'

    # Search for the envelope start
    envelope_start_seq = OP_FALSE + OP_IF + ORD + OP_1
    start_index = hex_string.find(envelope_start_seq)
    if start_index == -1:
        print("Envelope start sequence not found.")
        return None, None

    # Extract MIME type description
    mime_type_length_index = start_index + len(envelope_start_seq)
    mime_type_length_hex = hex_string[mime_type_length_index:mime_type_length_index + 2]
    mime_type_length = int(mime_type_length_hex, 16) * 2  # Length in characters
    mime_type_start = mime_type_length_index + 2
    mime_type_end = mime_type_start + mime_type_length
    mime_type_hex = hex_string[mime_type_start:mime_type_end]
    mime_type = bytes.fromhex(mime_type_hex).decode('ascii')
    print(f"MIME Type: {mime_type}")

    # Find and collect inscription data chunks
    data_start = mime_type_end + 2  # Skipping OP_0
    inscription_data = ''
    while hex_string[data_start:data_start + 2] != OP_ENDIF:
        opcode_hex = hex_string[data_start:data_start + 2]
        opcode = int(opcode_hex, 16)
        data_start += 2
        chunk_length = 0
        if '01' <= opcode_hex <= '4b':  # Direct push of 1-75 bytes
            chunk_length = opcode * 2  # Length in characters
        elif opcode_hex in [OP_PUSHDATA1, OP_PUSHDATA2, OP_PUSHDATA4]:
            length_bytes = 2 if opcode_hex == OP_PUSHDATA1 else 4 if opcode_hex == OP_PUSHDATA2 else 8
            chunk_length_hex = hex_string[data_start:data_start + length_bytes]
            # Convert hex string to byte array in little-endian format and get length
            chunk_length = int.from_bytes(bytes.fromhex(chunk_length_hex), 'little') * 2
            data_start += length_bytes
        else:
            print("Unexpected data format in inscription.")
            break

        chunk_start = data_start
        chunk_end = chunk_start + chunk_length
        inscription_data += hex_string[chunk_start:chunk_end]
        data_start = chunk_end

    # Return the MIME type and inscription data in hex format
    return mime_type, inscription_data


def inscription_data_to_file(mime_type, hex_string, output_file):
    # Convert hex string to bytes
    binary_data = bytes(int(hex_string[i:i+2], 16) for i in range(0, len(hex_string), 2))

    # Determine the file extension
    extension = mime_type_to_extension(mime_type)
    output_file_with_extension = f"{output_file}.{extension}"

    # Save binary data to a file
    with open(output_file_with_extension, 'wb') as file:
        file.write(binary_data)

    print(f"File saved as {output_file_with_extension}")

# Example usage
witness_data = get_witness_data_from_tx_id('265f9bdb256d8ec23328a80e7b52680fb0fdcc57061856352993939e8bc96898')
mime_type, inscription = find_envelope_and_inscription(witness_data)
if inscription:
    output_file = "inscription_file"  # Base name for the output file
    inscription_data_to_file(mime_type, inscription, output_file)