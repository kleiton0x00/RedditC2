import base64

#Function to xor encrypt a string
def xor_encrypt(plaintext, key):
    encrypted_text = ""
    for i in range(len(plaintext)):
        encrypted_text += chr(ord(plaintext[i]) ^ ord(key[i % len(key)]))
    return encrypted_text

#Function to base64 encode the string
def base64_encode(plaintext):
    return base64.b64encode(plaintext.encode())

#Function to encrypt the string
def encrypt(plaintext, key):
    encrypted_text = xor_encrypt(plaintext, key)
    return base64_encode(encrypted_text)

#Decryption

#Function to base64 decode the string
def base64_decode(encoded_text):
    return base64.b64decode(encoded_text).decode()

#Function to xor decrypt the string
def xor_decrypt(plaintext, key):
    decrypted_text = ""
    for i in range(len(plaintext)):
        decrypted_text += chr(ord(plaintext[i]) ^ ord(key[i % len(key)]))
    return decrypted_text

#Function to decrypt the string
def decrypt(encoded_text, key):
    decoded_text = base64_decode(encoded_text)
    return xor_decrypt(decoded_text, key)
