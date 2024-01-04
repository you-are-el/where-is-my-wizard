import ordinals_parser as ord
import math
import time
import sys
import random
import json
import os
import subprocess
from pprint import pformat

# Function to print like a typewriter
def typewriter_print(text, delay=0.04):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()  # Move to the next line

# Function for loading animation
def loading_animation(duration, interval=0.1):
    chars = "|/-\\"
    end_time = time.time() + duration

    while time.time() < end_time:
        for char in chars:
            sys.stdout.write('\r' + char)
            sys.stdout.flush()
            time.sleep(interval)

tx_id = 'c81229a4b6a35e338ba708afeb878995821834977b8f030b5dc5d4b55b64462e'
blockchain = ord.get_blockchain_info()
block = ord.get_block_data_from_tx_id(tx_id)
full_tx = ord.get_full_transaction_from_tx_id(tx_id)
witness = ord.get_witness_data_from_tx_id(tx_id)

# Let's Do a lil Magic
whererismywizard = [
    "  _      ____                 ____      __  ___       _      ___                 _____ ",
    " | | /| / / /  ___ _______   /  _/__   /  |/  /_ __  | | /| / (_)__ ___ ________/ /__ \\",
    " | |/ |/ / _ \\/ -_) __/ -_) _/ /(_-<  / /|_/ / // /  | |/ |/ / /_ // _ `/ __/ _  / /__/",
    " |__/|__/_//_/\\__/_/  \\__/ /___/___/ /_/  /_/\\_, /   |__/|__/_//__/\\_,_/_/  \\_,_/ (_)  ",
    "                                            /___/                                       "
]

# Print each line of the ASCII art using typewriter_print
for line in whererismywizard:
    typewriter_print(line, 0.002)

print("")
typewriter_print("There's a whisper going around that wizards dwell in the Bitcoin blockchain,")
typewriter_print("hidden within each and every Bitcoin node. They call themselves Taproot Wizards.")
typewriter_print("Our quest today: to uncover the secrets of Taproot Wizard #1620.")
typewriter_print(f"Rumor has it that this particular wizard was last seen in block number {block['height']}.")
typewriter_print("Let's gear up and dive into our local Bitcoin node to see if the legends hold any truth!")
print("")
time.sleep(1)

# Connect to node
typewriter_print(f"Connecting to local node...")
loading_animation(1)
print("")
typewriter_print(f"Connection to local node established.")
typewriter_print(f"Chain: {blockchain['chain']}")
typewriter_print(f"Current block height: {blockchain['blocks']}")
typewriter_print(f"Size on disk: {blockchain['size_on_disk']}")
typewriter_print(f"Node operator: @you_are_el")
print("")
time.sleep(1)

# The block
# Print the block number and visualize the block 

typewriter_print(f"Fetching block {block['height']}")
print("")
# The Block
# The Block ASCII art in the new format
the_block = [
    " ________         ___  __         __  ",
    "/_  __/ /  ___   / _ )/ /__  ____/ /__",
    " / / / _ \/ -_) / _  / / _ \/ __/  '_/",
    "/_/ /_//_/\__/ /____/_/\___/\__/_/\_\ ",
    "                                      "
]

# Print each line of the ASCII art using typewriter_print
for line in the_block:
    typewriter_print(line, 0.002)

# Block data
block_height = block['height']
tx_count = block['nTx']

# Calculate the dimensions of the square block
dimension = int(math.ceil(math.sqrt(tx_count)))

# Adjust for character height-width ratio
# This ratio might need fine-tuning based on your specific terminal font and settings
ratio = 2
adjusted_dimension = int(math.ceil(dimension * ratio))

# Determine random position for the special block
special_block_row = random.randint(0, dimension - 1)
special_block_col = random.randint(0, adjusted_dimension - 1)

# ASCII Art for Block Height
typewriter_print(f"Block #: {block_height}")

# ASCII Art for 2D block in typewriter style
for row in range(dimension):
    line = ''
    for col in range(adjusted_dimension):
        if row == special_block_row and col == special_block_col:
            line += '□'
        else:
            line += '■'
    if row == special_block_row:
        line += f" <- What's this? This transaction seems unusual..."
    typewriter_print(line, 0.001)

print("")
typewriter_print(f"Block was successfully fetched")
typewriter_print("Let's delve into this peculiar transaction and uncover its secrets.")
print("")
time.sleep(1)

# The transaction
the_transaction = [
    " ________         ______                           __  _         ",
    "/_  __/ /  ___   /_  __/______ ____  ___ ___ _____/ /_(_)__  ___ ",
    " / / / _ \\/ -_)   / / / __/ _ `/ _ \\(_-</ _ `/ __/ __/ / _ \\/ _ \\",
    "/_/ /_//_/\\__/   /_/ /_/  \\_,_/_//_/___/\\_,_/\\__/\\__/_/\\___/_//_/",
    "                                                                  "
]

# Print each line of the ASCII art using typewriter_print
for line in the_transaction:
    typewriter_print(line, 0.002)


typewriter_print(f"Fetching transaction:")
typewriter_print(f"{tx_id}")
loading_animation(1)
print("")
typewriter_print(f"Transaction successfully fetched.")
time.sleep(1)

print("")
typewriter_print(pformat(full_tx), 0.00009)
print("")
time.sleep(1)
typewriter_print("Aha! We're hot on the wizard's trail now.")
typewriter_print("It seems our mystical being is cloaked in the witness data of the transaction.")
typewriter_print("Let the extraction begin!")
time.sleep(1)

# The witness data
# The Witness Data ASCII art in the new format
the_witness_data = [
    " ________         _      ___ __                 ",
    "/_  __/ /  ___   | | /| / (_) /____  ___ ___ ___",
    " / / / _ \\/ -_)  | |/ |/ / / __/ _ \\/ -_|_-<(_-<",
    "/_/ /_//_/\\__/   |__/|__/_/\\__/_//_/\\__/___/___/",
    "                                                "
]

# Print each line of the ASCII art using typewriter_print
for line in the_witness_data:
    typewriter_print(line, 0.002)

typewriter_print(f"Extracting witness data.")
loading_animation(1)
print("")
typewriter_print(f"Witness data successfully extracted.")
time.sleep(1)

print("")
typewriter_print(witness, 0.00009)
print("")

typewriter_print("Amidst this clutter of characters, our wizard awaits in the inscription.")
typewriter_print("Let's filter out the noise.")
print("")

# Cleaning of the witness data
# The inscription data
the_inscription_data = [
    " ________         ____                 _      __  _         ",
    "/_  __/ /  ___   /  _/__  ___ ________(_)__  / /_(_)__  ___ ",
    " / / / _ \\/ -_) _/ // _ \\(_-</ __/ __/ / _ \\/ __/ / _ \\/ _ \\",
    "/_/ /_//_/\\__/ /___/_//_/___/\\__/_/ /_/ .__/\\__/_/\\___/_//_/",
    "                                     /_/                    "
]

# Print each line of the ASCII art using typewriter_print
for line in the_inscription_data:
    typewriter_print(line, 0.002)

print("")
typewriter_print(f"Extracting the inscription from the witness data.")
loading_animation(1)
print("")
typewriter_print(f"Inscription data successfully extracted.")

mime_type, inscription_data = ord.find_envelope_and_inscription(witness)

time.sleep(1)
print("")
typewriter_print(inscription_data, 0.00009)
print("")
time.sleep(1)

typewriter_print("There it is. The wizard! Summoned from the depths of the blockchain.")
typewriter_print("Majestic right?")
time.sleep(1)
typewriter_print("What? You can't see it?")
typewriter_print("It's literally right there in front of you.")
time.sleep(1)
typewriter_print("Oh, right! You need this magical code converted to a JPEG to make it")
typewriter_print("visible to the mortal eye!")
time.sleep(1)
typewriter_print("Ok one second...")
typewriter_print("Let's do a lil magic and morph these mysterious hexes into a JPEG.")
loading_animation(3)
print("")

# Convert to file (the magic) 

# Convert hex string to bytes
binary_data = bytes(int(inscription_data[i:i+2], 16) for i in range(0, len(inscription_data), 2))

# Determine the file extension
extension = ord.mime_type_to_extension(mime_type)  # Ensure this function exists to determine the correct file extension
output_file_with_extension = f"wizard.{extension}"

# Save binary data to a file
with open(output_file_with_extension, 'wb') as file:
    file.write(binary_data)

# Function to open the file with the default application
def open_file(file_path):
    if os.name == 'nt':  # Windows
        os.startfile(file_path)
    elif os.name == 'posix':  # macOS, Linux, Unix, etc.
        if sys.platform == 'darwin':  # macOS
            subprocess.run(['open', file_path])
        else:  # Linux and Unix
            subprocess.run(['xdg-open', file_path])

# Open the file
open_file(output_file_with_extension)

typewriter_print(f"There you go. A wizard forever stored on this and every Bitcoin node.")
time.sleep(1)
print("")
typewriter_print("Curious how this magic works? Want to summon a Taproot Wizard yourself?")
typewriter_print("Visit whereismywizard.xyz and join the circle of blockchain sorcerers.")
time.sleep(1)
print("")
typewriter_print(f"Brought to you by @you_are_el")
typewriter_print(f"Inspired by Taproot Wizards")

# Join us
join_us = [
    "     __     _               ",
    " __ / /__  (_)__    __ _____",
    "/ // / _ \\/ / _ \\  / // (_-<",
    "\\___/\\___/_/_//_/  \\_,_/___/"
]

# Print each line of the ASCII art using typewriter_print
for line in join_us:
    typewriter_print(line, 0.002)

print("")