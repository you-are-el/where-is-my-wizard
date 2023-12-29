import requests
import streamlit as st
from annotated_text import annotated_text
import streamlit.components.v1 as components
import pandas as pd
import ordinals_parser as ord

class Tweet(object):
    def __init__(self, s, embed_str=False):
        if not embed_str:
            # Use Twitter's oEmbed API
            # https://dev.twitter.com/web/embedded-tweets
            api = "https://publish.twitter.com/oembed?url={}".format(s)
            response = requests.get(api)
            self.text = response.json()["html"]
        else:
            self.text = s

    def _repr_html_(self):
        return self.text

    def component(self):
        return components.html(self.text, height=1100)

def display_inscription_data(mime_type, hex_string):
    # Convert hex string to bytes
    binary_data = bytes(int(hex_string[i:i+2], 16) for i in range(0, len(hex_string), 2))

    if mime_type.startswith('image/'):
        st.image(binary_data)
    elif mime_type.startswith('audio/'):
        st.audio(binary_data)
    elif mime_type.startswith('video/'):
        st.video(binary_data)
    else:
        st.text(binary_data.decode())

def annotate_envelope_and_inscription(hex_string):
    # Define the envelope format and opcodes in hex
    opcodes = {
        '00': 'OP_FALSE',
        '63': 'OP_IF',
        '036f7264': 'OP_PUSH "ord"',
        '0101': 'OP_PUSH 1',
        '00': 'OP_PUSH 0',
        '4c': 'OP_PUSHDATA1',
        '4d': 'OP_PUSHDATA2',
        '4e': 'OP_PUSHDATA4',
        '68': 'OP_ENDIF'
    }

    envelope_start_seq = '00' + '63' + '036f7264' + '0101'
    start_index = hex_string.find(envelope_start_seq)

    if start_index == -1:
        print("Envelope start sequence not found.")
        return []

    annotated = []
    last_was_data_chunk = False
    is_first_00 = True

    # Include the part of the string before the envelope start sequence
    if start_index > 0:
        annotated.append(hex_string[:start_index])

    i = start_index

    while i < len(hex_string):
        matched_opcode = None
        for code, name in opcodes.items():
            code_len = len(code)
            if hex_string[i:i+code_len] == code:
                matched_opcode = code
                if code == '00' and is_first_00: # First 00 is OP_FALSE, following 00s are OP_PUSH 0
                    is_first_00 = False
                    annotated.append((hex_string[i:i+code_len], 'OP_FALSE'))
                    i += code_len
                else:
                  annotated.append((hex_string[i:i+code_len], name))
                  i += code_len

                # Check for OP_ENDIF following a data chunk or direct push
                if code == '68' and last_was_data_chunk:
                    return annotated
                last_was_data_chunk = False
                break

        # Check for direct push opcodes (1-75 bytes)
        if not matched_opcode and '01' <= hex_string[i:i+2] <= '4b':
            opcode_hex = hex_string[i:i+2]
            chunk_length = int(opcode_hex, 16) * 2  # Convert to number of characters
            chunk_start = i + 2
            chunk_end = chunk_start + chunk_length
            annotated.append((hex_string[chunk_start:chunk_end], f'Direct Data Push: {chunk_length // 2} bytes'))
            i = chunk_end
            last_was_data_chunk = True
            continue
        
        # Handle MIME type extraction and data chunk annotation
        if matched_opcode and matched_opcode == '0101':
                # Extract MIME type after OP_1
                mime_type_length_hex = hex_string[i:i+2]
                mime_type_length = int(mime_type_length_hex, 16) * 2
                mime_type_start = i + 2
                mime_type_end = mime_type_start + mime_type_length
                mime_type_hex = hex_string[mime_type_start:mime_type_end]
                mime_type = bytes.fromhex(mime_type_hex).decode('ascii')
                annotated.append((mime_type_hex, f'MIME Type: "{mime_type}"'))
                i = mime_type_end
        
        if matched_opcode and matched_opcode in ['4c', '4d', '4e']:
            # Calculate data chunk length for PUSHDATA opcodes
            length_bytes = 2 if matched_opcode == '4c' else 4 if matched_opcode == '4d' else 8
            chunk_length_hex = hex_string[i:i+length_bytes]
            chunk_length = int.from_bytes(bytes.fromhex(chunk_length_hex), 'little')
            annotated.append((chunk_length_hex, f'Data Length: {chunk_length} bytes'))

            # Calculate the actual start and end of the data chunk
            chunk_start = i + length_bytes
            chunk_end = chunk_start + chunk_length * 2
            annotated.append((hex_string[chunk_start:chunk_end], 'Data Chunk'))
            i = chunk_end
            last_was_data_chunk = True
            continue

        if not matched_opcode:
            # If no opcode is matched, increment by 2 (smallest opcode length)
            annotated.append(hex_string[i:i+2])
            i += 2

    return annotated

####################################################################################################################################
### Title and Intro                                                                                                              ###
####################################################################################################################################
        
st.title("Where Is My Taproot Wizard?")
st.subheader("An educational tool to help you find your wizard on the Bitcoin blockchain")
st.caption("By [You Are El](https://twitter.com/you_are_el)")
st.write("Inscriptions inscribe sats with arbitrary content, creating bitcoin-native digital artifacts, more commonly known as NFTs (Source: [Ordinal Theory Handbook](https://docs.ordinals.com/inscriptions.html)). \
         One of the most well known collections of inscriptions on the Bitcoin blockchain is the [Taproot Wizards](https://taprootwizards.com/collection) collection which we will take a closer look at today. \
         Inscriptions, compared to many other NFTs, are stored directly on the blockchain. You will hear people say that an inscription is encoded forever on the blockchain. But what does that mean exactly? \
         In this Streamlit app I want to show you where exactly your wizard is encoded on the blockchain to understand what it means that inscriptions and the Taproot Wizards in particular are forever stored on every \
         Bitcoin node.")

st.write("For the sake of simplicity, this demo connects to publicly available APIs to retrieve the inscription data (i.e. a public bitcoin node). However, this process works exactly the same on your own Bitcoin node.")

st.write("This demo is set up to work with the [Taproot Wizards](https://taprootwizards.com/collection) collection. However, it does support almost any other inscriptions as well, except for recursive inscriptions. If you want to explore other inscriptions, \
         you can paste a transaction ID into the text field further down on this website. You can explore other inscriptions on ordinals explorers like [ord.io](https://www.ord.io).")

st.header("Encoded Forever on Bitcoin") 
st.write("You will find posts like this all over Odrinals X communities and it is one of [Udi Wertheimer's](https://twitter.com/udiWertheimer) favorite things to point out. Wizards (and inscriptions in general) are forever encoded on Bitcoin. \
         But what does that mean exactly? Does that mean that all these inscriptions are literally stored on Bitcoin like files on a computer? Yes, kind of. This web app will teach you where and how they are stored exactly. \
        Let's take a look at the post below.")

t = Tweet("https://twitter.com/udiWertheimer/status/1739900877803049393").component()
st.write("So apparently this wizard is encoded forever on bitcoin. Sidenote: This specific wizard belongs to [Billy Markus](https://billym2k.net/) the creator of Dogecoin. Let's see if we can actually find it \
         on the blockchain.")

####################################################################################################################################
### Oh Wizard Where Art Thou?                                                                                                    ###
####################################################################################################################################

st.header("Oh Wizard Where Art Thou?")
st.write("Ok so Udi is giving us some clues here. The wizard is encoded forever on bitcoin block 783077. Let's have a look at that block below and see if we can spot the wizard.")

st.components.v1.iframe("https://bits.monospace.live/block/height/783077", height=400, scrolling=True)

st.markdown("Can you spot the the wizard? No? That's ok. Udi also said it is encoded. That means it is somehow stored in a (usually) non-human readable format. Let's explore the block some more. The little squares in that block \
         are all the individual transactions. One of these transaction apparently contains the wizard. We can hover with the mouse over all the different transactions and try to find the one with our wizard in it. \
         Still, by just exploring the block this way, it's hard to find the wizard. Let's instead try to find the transaction that contains the wizard directly. Here as well Udi is giving us a clue. The wizard is \
         hidden in the transaction with the ID **'ef207ae72e81c068142ab6ea03f2549e8c6edb2e96050ae1616b65ce3347d1edi0'**. However, that is not quite correct. The ID Udi provided is actually the inscription ID. We can check \
         this by visiting [ord.io](https://www.ord.io/) and searching for the ID. You can do this below, just enter the ID into the search bar.")

st.components.v1.iframe("https://www.ord.io/", height=800, scrolling=True)
st.caption("This is the website ord.io. It is an ordinals explorer. Try putting in the Inscription ID from above into the search bar. You can also search for 'Taproot Wizards' to see the full collection.")

st.markdown("Notice how the ID Udi provided in the post, is actually the Inscription ID (the first entry below the image on ord.io). If we scroll down a bit on the page, we can find the actual transaction ID \
         of the 'CREATION TRANSACTION' which is actually really similar to the inscription ID: **'ef207ae72e81c068142ab6ea03f2549e8c6edb2e96050ae1616b65ce3347d1ed'**. It is just missing the two characters 'i0' at the end. \
         This is the ID we need to find the transaction on the blockchain which inscribed the wizard image. Next, let's have a look at the transaction in detail.")

####################################################################################################################################
### Interrogating the Witness                                                                                                    ###
####################################################################################################################################

st.header("Interrogating the Witness")
st.write("We are closing in on the wizard. However, now comes the complicated part. Let's reiterate for a second. If the wizard is actually stored on the blockchain, in a specific block, within a specific transaction, \
         then we should be able to find it there somehow. However, there won't be an actual image file in the transaction. Instead, the image data is encoded in the transaction in a non-human readable format. So in order \
         to find the wizard we need to know where to look. We will start by looking at the transaction below and the we will gradually dissect it to find our wizard.")

st.write("We are using the mempool.space API to retrieve the transaction data. You can find the API documentation [here](https://mempool.space/api). If we were running our own Bitcoin node, we could also use the \
         Remote Procedure Call (RPC) protocol to retrieve the transaction data (we will do this in another demo). Let's load the transaction below by pasting the transaction ID into the text field below.")

tx_id = st.text_input('Transcation ID', 'ef207ae72e81c068142ab6ea03f2549e8c6edb2e96050ae1616b65ce3347d1ed')
st.caption('Here you can paste the transaction ID from above. The transaction ID from the transaction that inscribed our doge wizard is already filled in. But you can also paste any other transaction ID from your favorite wizard here.')

full_txs = ord.get_full_transaction_from_tx_id(tx_id)
witness_data = ord.get_witness_data_from_tx_id(tx_id)

st.markdown("The following is the full transaction in JSON format. It shows all the different parts of the transaction. It would take too much time to explain all these different parts. Luckily the \
         [Ordinal Theory Handbook](https://docs.ordinals.com/guides/inscriptions.html) tells us that 'inscription content is included in transaction witnesses [...]'. We can find the witness data in \
         the JSON below by unfolding the JSON, then unfolding the `vin` object (then the `0` object) and then unfolding the `witness` object. I recommend to explore the JSON a bit yourself. Try to find the \
            witness data. Afterwards fold the JSON again to make the rest of the website more readable. Click on the little green arrow below to unfold the JSON.")

st.json(full_txs, expanded=False)
st.caption('This is the complete transaction in JSON format which we retrieved from the [mempool.space/api](https://mempool.space/api)')

st.write("For better readability, the witness data is extracted below and displayed in a separate text area. You can check that the witness data is the same as in the JSON above.")

st.text_area("Witness Data: This data is in hexadecimal format. This has the inscription encoded (believe me).", witness_data, height=400)

st.write("Ok, so WTF is this? This is just a lot of mubmo jumbo. How are we supposed to find our wizard in this? Let's take a closer look at the witness data. I promise you, the wizard is in there somewhere.")
st.write("To continue, we need some more information about how the wizard is encoded in the witness data. First of all, the witness data is encoded using [hexadecimal](https://en.wikipedia.org/wiki/Hexadecimal) values. \
         'Hexadecimal is used in the transfer encoding Base16, in which each byte of the plaintext is broken into two 4-bit values and represented by two hexadecimal digits' (Source: [Wikipedia](https://en.wikipedia.org/wiki/Hexadecimal)). \
         Furthermore we need to know that inscriptions use a specific format that we have to look for in this witness data. From the Ordinal Theory Handbook we learn that 'inscription content is serialized \
         using data pushes within unexecuted conditionals, called 'envelopes'. Envelopes consist of an OP_FALSE OP_IF … OP_ENDIF wrapping any number of data pushes. \
         Because envelopes are effectively no-ops, they do not change the semantics of the script in which they are included, and can be combined with any other locking script (Source: [Ordinal Theory \
         Handbook](https://docs.ordinals.com/inscriptions.html)). If this sounds very confusing, don't worry. We will look at OP codes next.")

st.write("A text inscription containing the string 'Hello, world!' is serialized as follows:")

code = '''
OP_FALSE
OP_IF
  OP_PUSH "ord"
  OP_PUSH 1
  OP_PUSH "text/plain;charset=utf-8"
  OP_PUSH 0
  OP_PUSH "Hello, world!"
OP_ENDIF
'''
st.code(code)
st.caption("Example taken from the [Ordinal Theory Handbook](https://docs.ordinals.com/inscriptions.html)")

st.write("Since we are looking for an image our envelope will look a bit different:")

code = '''
OP_FALSE
OP_IF
  OP_PUSH "ord"
  OP_PUSH 1
  OP_PUSH "image/webp"
  OP_PUSH 0
  OP_PUSH <IMAGE DATA>
OP_ENDIF
'''
st.code(code)
st.caption("Since our wizard was inscribed as a webp image file, the envelope will look like this. The code OP_PUSH <IMAGE DATA> is a placeholder for where the actual image data will be. This will be explained further below.")


st.markdown("Ok, so what we are technically doing now is looking for the envelope in the witness data. If we can identify the parts of the envelope, we first of all know that there is an inscription at all. \
         And furthermore we can identify the image data to reconstruct our wizard. In order to identify the envelope, we need to know how the opcodes look in hexadecimal format. We can find this information \
         in the following [Bitcoin Wiki](https://en.bitcoin.it/wiki/Script). Here we can see for example that the `OP_FALSE` opcode is represented by the hexadecimal value `0x00` (or just `00`) and the `OP_IF` \
            opcode is represented by the hexadecimal value `0x63` (or just `63`). Let's use this knowledge to find the envelope in the witness data.")

st.header("Finding the Envelope")

st.write("Before we start looking for the envelope, we need to define all of the opcodes we will need to find it. Let's have a look at the opcodes and their hexadecimal representation below.")

code = '''
# Define the envelope format and opcodes
OP_FALSE = '00'
OP_IF = '63'
OP_PUSH "ord" = '036f7264'
OP_PUSH_1 = '0101'
OP_PUSH_0 = '00'
OP_ENDIF = '68'
'''
st.code(code, language='python')

# Define the envelope format and opcodes
OP_FALSE = '00'
OP_IF = '63'
OP_PUSH_ORD = '036f7264'
OP_PUSH_1 = '0101'
OP_PUSH_0 = '00'
OP_ENDIF = '68'

st.markdown("We have defined the necessary opcodes above in hexadecimal format. Notice that `OP_FALSE` and `OP_PUSH 0` have the same hexadecimal representation. While some of the opcodes have a specific \
            hexadecimal value assigned to them, some are not predefined. You might be wondering why \
            `OP_PUSH 'ord'` translates to `036f7264`. To understand this we need to understand the `OP_PUSH` opcode. This opcode pushes data onto the stack. That just means it contains literally the data that \
            will be written to the blockchain. For this opcode the first byte (meaning the first two characters of the string) define the size of the data that is pushed. In our case we want to literally \
            write the word `'ord'`. This word contains three bytes of data. So we start the `OP_PUSH` with a `03` indicating that three bytes of data will be pushed. The next three bytes (or three pairs of two characters) \
            are literally the word 'ord' in hexadecimal format. If we interpret `'6f7264'` in ASCII: `'6f'` = 'o', `'72'` = 'r', `'64'` = 'd'. That is all we need for now to identify the start of the envelope. \
            Notice that we have not defined `OP_PUSH 'image/webp'` and `OP_PUSH <IMAGE DATA>`. These two are not static and will change depending on the \
            inscription. We will identify these opcodes on the fly after we have found the start of the envelope while parsing the data. However, you already know how to identify `OP_PUSH 'image/webp'`. \
            It works analogous to the `OP_PUSH 'ord'`. Let's start by searching for the envelope start sequence.")


# Search for the envelope start
envelope_start_seq = OP_FALSE + OP_IF + OP_PUSH_ORD + OP_PUSH_1

st.write("We know that the envelope starts with:")
code = '''
OP_FALSE
OP_IF
  OP_PUSH "ord"
  OP_PUSH 1
'''
st.code(code)
st.write("This translates to:")
st.code(envelope_start_seq)
st.caption("We are literally just connecting the hexadecimal values of the opcodes together: OP_FALSE + OP_IF + OP_PUSH 'ord' + OP_PUSH 1 translates to 00 + 63 + 036f7264 + 0101")


st.subheader("Parsing the Witness Data")
st.markdown("Now that we have our start sequence, we can find it in the witness data. The annotation below shows the first 1500 characters of the witness data (for better readability and faster loading, the full \
            witness data is a lot longer and depends on the size of the data that is inscribed).\
         We can see that after the first few lines, the witness data starts with the \
         envelope start sequence: `OP_FALSE` (00), followed by `OP_IF` (63), followed by `OP_PUSH 'ord'` (036f7264), followed by `OP_PUSH 1` (0101)  After the `OP_PUSH 1` opcode, we can the see opcode that defines \
            the MIME type of the inscription. In the case of our wizard this will say 'image/webp' and defines how to interpret the data. After that we get the `OP_PUSH 0` code. This code indicates that now the actual \
            inscription data follows. The format for the inscription data is defined by one byte defining how many bytes will be used to encode the next chunk of the data. In the case of our doge wizard we get `4d`. \
            A look at the [Bitcoin Wiki](https://en.bitcoin.it/wiki/Script) tells us that `4d` stands for the opcode `OP_PUSHDATA2` and means 'The next two bytes contain the number of bytes to be pushed onto the stack \
            in little endian order'. The endian order just describes in which order the following bytes are to be read. Let's look at the next two bytes: `0802`. The little endian order tells us to read them as `0208` \
            which converts to 520 in decimal values. This means that the next 520 bytes will be actual inscription data. As 1 byte needs two characters in hexadecimal this means that literally the next 1040 characters in the \
            witness data are part of the actual wizard image. You can check all the opcodes and lengths in the annotation below. This pattern is repeated until the end of \
         the inscription data. The inscription data is then followed by the `OP_ENDIF` opcode. 520 bytes is the largest number of bytes a standard tx can push onto the stack at once. Ord splits its inscriptions \
         up into 520 byte pieces like this. You can see the first 520 byte chunk below, followed by the second one. There are a lot more chunks after that which we will not display here. After the last chunk \
         we would find the `OP_ENDIF` opcode.")

witness_data_first_1500 = witness_data[:1500]
annotated = annotate_envelope_and_inscription(witness_data_first_1500)
annotated_text(annotated)
st.caption("This is an annotation of the first 1500 characters of the witness data.")

st.subheader("So where is the wizard now?")
st.write("So where is the wizard now, you might ask? Well, it is in all these data chunks. If we literally copy all these individual data chunks and concatenate them, we will get the wizard image encoded in hexadecimal format. \
         We are almost done. Let's do a lil magic!")


st.header("Wizard, Come Out, Wherever You Are")
st.write("In our example above we only displayed the first two chunks of data that make up our wizard. In the actual transaction the witness data is a lot longer and has many of these data chunks. \
         To make things easier this application extracted all the individual chunks exactly in the same way as you can see in the annotation. Below you find a text field with exactly all this data concatenated. \
         You can check the first lines of the data against the annotation above. I promise you it is literally the same data. The last step is to convert this large string of text into byte data and display it as an image.  \
         Below you can see the result of that. And to proof that I am not just loading a random image into this website, please copy and paste the text into a random hex to image converter below.")

mime_type, inscription = ord.find_envelope_and_inscription(witness_data)

st.text_area("All the inscription data concatenated. You can paste this data into any hex to image converter.", inscription, height=400)

st.write("I have loaded a random hex to image converter below. You can copy and paste the text from the text area above into this converter to see the wizard image. You can also search for other hex to image converters \
         on Google.")
st.components.v1.iframe("https://codepen.io/abdhass/full/jdRNdj", height=800, scrolling=True)
st.caption("This is a hex to image converter. You can copy and paste the text from the text area below into this converter to see the wizard image.")
st.write("As you can see the image is literally on the blockchain. It is just encoded in a non-human readable format and hidden in the witness data of the transaction. But it is there. And it will be there forever.")


st.header("The Wizard (Inscription)")
if inscription:
  display_inscription_data(mime_type, inscription)

st.write("And this my fellow wizards is how Taproot Wizards are literally stored on the Bitcoin blockchain forever. As long as a node is running, the wizard will be there. \
         If that isn't magic, I don't know what is.")
  
st.header("How To Use This Tool")
st.write("This application is meant to be an educational tool to help you understand how inscriptions are stored on the Bitcoin blockchain. It uses the doge wizard as an example inscription. However, the tool technically \
         works with all inscriptions as long as they are text, image, video, or audio based. Recursive inscriptions are not yet supported. You can scroll up to the text field for the transaction ID, paste any other \
         transaction ID for an inscription you would like to explore and hit enter. Keep in mind that the application might break due to the different formats of inscriptions. If you encounter problems or just want to leave a like, please \
         hit me up on X ([@you_are_el](https://twitter.com/you_are_el)).")
st.write("Recursive inscriptions are not yet supported.")
st.header("Acknowledgements")
st.write("I could have never developed this fun little project without the help of some very smart people. \
         Thanks to all the contributors of the [ord github repo](https://github.com/ordinals/ord) and for writing a stellar documentation. \
         Thanks to the wizards at [Taproot Wizards](https://taprootwizards.com/) for encouraging fun on Bitcoin which motivated me in the first place to explore this topic.\
         Thanks to [Jan](https://twitter.com/nonfungible_jan) and [Tyler](https://twitter.com/Dr_DAO_) for the Youtube series [Technically Bitcoin](https://www.youtube.com/@TechnicallyBitcoin). \
         A special thanks to [Greg](https://twitter.com/gm7t2) in The Ordicord Discord for the explanations of the opcodes and how to parse them. \
         ")