#!/usr/bin/env python
# ----------------- Header Files ---------------------#

import sys
import random
import argparse
import logging
import os
import math
import hashlib
import binascii

import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import *
from PIL import Image
from Crypto.Cipher import AES
import numpy as np

global password 

def load_image(name):
    return Image.open(name)

# ----------------- Functions for encryption ---------------------#
def prepare_message_image(image, size):
    if size != image.size:
        image = image.resize(size, Image.ANTIALIAS)
    return image

def generate_secret(size, secret_image=None):
    width, height = size
    new_secret_image = Image.new(mode="RGB", size=(width * 2, height * 2))

    for x in range(0, 2 * width, 2):
        for y in range(0, 2 * height, 2):
            color1 = np.random.randint(255)
            color2 = np.random.randint(255)
            color3 = np.random.randint(255)
            new_secret_image.putpixel((x, y), (color1, color2, color3))
            new_secret_image.putpixel((x + 1, y), (255 - color1, 255 - color2, 255 - color3))
            new_secret_image.putpixel((x, y + 1), (255 - color1, 255 - color2, 255 - color3))
            new_secret_image.putpixel((x + 1, y + 1), (color1, color2, color3))
                
    return new_secret_image

def generate_ciphered_image(secret_image, prepared_image):
    width, height = prepared_image.size
    ciphered_image = Image.new(mode="RGB", size=(width * 2, height * 2))
    for x in range(0, width * 2, 2):
        for y in range(0, height * 2, 2):
            sec = secret_image.getpixel((x, y))
            msssg = prepared_image.getpixel((int(x / 2), int(y / 2)))
            color1 = (msssg[0] + sec[0]) % 256
            color2 = (msssg[1] + sec[1]) % 256
            color3 = (msssg[2] + sec[2]) % 256
            ciphered_image.putpixel((x, y), (color1, color2, color3))
            ciphered_image.putpixel((x + 1, y), (255 - color1, 255 - color2, 255 - color3))
            ciphered_image.putpixel((x, y + 1), (255 - color1, 255 - color2, 255 - color3))
            ciphered_image.putpixel((x + 1, y + 1), (color1, color2, color3))
                
    return ciphered_image

def generate_image_back(secret_image, ciphered_image):
    width, height = secret_image.size
    new_image = Image.new(mode="RGB", size=(int(width / 2), int(height / 2)))
    for x in range(0, width, 2):
        for y in range(0, height, 2):
            sec = secret_image.getpixel((x, y))
            cip = ciphered_image.getpixel((x, y))
            color1 = (cip[0] - sec[0]) % 256
            color2 = (cip[1] - sec[1]) % 256
            color3 = (cip[2] - sec[2]) % 256
            new_image.putpixel((int(x / 2), int(y / 2)), (color1, color2, color3))
               
    return new_image

#------------------------Encryption -------------------#
def level_one_encrypt(Imagename):
    message_image = load_image(Imagename)
    size = message_image.size
    width, height = size

    secret_image = generate_secret(size)
    secret_image.save("secret.jpeg")

    prepared_image = prepare_message_image(message_image, size)
    ciphered_image = generate_ciphered_image(secret_image, prepared_image)
    ciphered_image.save("2-share_encrypt.jpeg")

# -------------------- Construct Encrypted Image  ----------------#
def construct_enc_image(ciphertext, relength, width, height):
    asciicipher = binascii.hexlify(ciphertext).decode('utf-8')

    def replace_all(text, dic):
        for i, j in dic.items():
            text = text.replace(i, j)
        return text

    # use replace function to replace ascii cipher characters with numbers
    reps = {'a': '1', 'b': '2', 'c': '3', 'd': '4', 'e': '5', 'f': '6', 'g': '7', 'h': '8', 'i': '9', 'j': '10', 'k': '11', 'l': '12', 'm': '13', 'n': '14', 'o': '15', 'p': '16', 'q': '17', 'r': '18', 's': '19', 't': '20', 'u': '21', 'v': '22', 'w': '23', 'x': '24', 'y': '25', 'z': '26'}
    asciiciphertxt = replace_all(asciicipher, reps)

    # construct encrypted image
    step = 3
    encimageone = [asciiciphertxt[i:i + step] for i in range(0, len(asciiciphertxt), step)]
    # if the last pixel RGB value is less than 3-digits, add a digit a 1
    if int(encimageone[len(encimageone) - 1]) < 100:
        encimageone[len(encimageone) - 1] += "1"
    # check to see if we can divide the string into partitions of 3 digits. if not, fill in with some garbage RGB values
    if len(encimageone) % 3 != 0:
        while (len(encimageone) % 3 != 0):
            encimageone.append("101")

    encimagetwo = [(int(encimageone[int(i)]), int(encimageone[int(i + 1)]), int(encimageone[int(i + 2)])) for i in range(0, len(encimageone), step)]
    print(len(encimagetwo))
    while (int(relength) != len(encimagetwo)):
        encimagetwo.pop()

    encim = Image.new("RGB", (int(width), int(height)))
    encim.putdata(encimagetwo)
    encim.save("visual_encrypt.jpeg")

#------------------------- Visual-encryption -------------------------#
def encrypt(imagename, password):
    plaintext = list()
    plaintextstr = ""

    im = Image.open(imagename) 
    pix = im.load()

    width = im.size[0]
    height = im.size[1]
    
    # break up the image into a list, each with pixel values and then append to a string
    for y in range(0, height):
        for x in range(0, width):
            print(pix[x, y]) 
            plaintext.append(pix[x, y])
    print(width)
    print(height)

    # add 100 to each tuple value to make sure each are 3 digits long.  
    for i in range(0, len(plaintext)):
        for j in range(0, 3):
            aa = int(plaintext[i][j]) + 100
            plaintextstr = plaintextstr + str(aa)

    # length save for encrypted image reconstruction
    relength = len(plaintext)

    # append dimensions of image for reconstruction after decryption
    plaintextstr += "h" + str(height) + "h" + "w" + str(width) + "w"

    # make sure that plantextstr length is a multiple of 16 for AES.  if not, append "n". 
    while len(plaintextstr) % 16 != 0:
        plaintextstr = plaintextstr + "n"

    # convert the plaintext string to bytes
    plaintext_bytes = plaintextstr.encode('utf-8')

    # convert the IV to bytes and ensure it is 16 bytes long
    iv = b'This is an IV456'
    
    # encrypt plaintext
    obj = AES.new(password, AES.MODE_CBC, iv)
    ciphertext = obj.encrypt(plaintext_bytes)

    # write ciphertext to file for analysis
    cipher_name = imagename + ".crypt"
    with open(cipher_name, 'wb') as g:
        g.write(ciphertext)

    # Extract the directory from the uploaded image's path
    image_directory = os.path.dirname(imagename)

    # Save images in the same directory
    secret_image = generate_secret(im.size)
    secret_image.save(os.path.join(image_directory, "secret.jpeg"))

    prepared_image = prepare_message_image(im, im.size)
    ciphered_image = generate_ciphered_image(secret_image, prepared_image)
    ciphered_image.save(os.path.join(image_directory, "2-share_encrypt.jpeg"))

    construct_enc_image(ciphertext, relength, width, height)
    print("Visual Encryption done.......")
    level_one_encrypt("visual_encrypt.jpeg")
    print("2-Share Encryption done.......")


# ---------------------- decryption ---------------------- #
import os
from PIL import Image
from Crypto.Cipher import AES

def decrypt(ciphername, password):
    # Extract the directory from the uploaded image's path
    image_directory = os.path.dirname(ciphername)

    # Open the images (make sure to use the correct paths)
    secret_image = Image.open(os.path.join(image_directory, "secret.jpeg"))
    ima = Image.open(os.path.join(image_directory, "2-share_encrypt.jpeg"))
    
    # Generate the image back and save it in the same directory
    new_image = generate_image_back(secret_image, ima)
    new_image_path = os.path.join(image_directory, "2-share_decrypt.jpeg")
    new_image.save(new_image_path)
    print("2-share Decryption done....")

    # Open and read the ciphertext file in binary mode
    with open(ciphername, 'rb') as cipher:
        ciphertext = cipher.read()

    # Convert the IV to bytes and ensure it is 16 bytes long
    iv = b'This is an IV456'

    # Decrypt ciphertext with password
    obj2 = AES.new(password, AES.MODE_CBC, iv)
    decrypted = obj2.decrypt(ciphertext)

    # Parse the decrypted text back into integer string
    decrypted = decrypted.replace(b"n", b"").decode('utf-8')

    # Extract dimensions of images
    newwidth = decrypted.split("w")[1]
    newheight = decrypted.split("h")[1]

    # Replace height and width with empty space in decrypted plaintext
    heightr = "h" + str(newheight) + "h"
    widthr = "w" + str(newwidth) + "w"
    decrypted = decrypted.replace(heightr, "")
    decrypted = decrypted.replace(widthr, "")

    # Reconstruct the list of RGB tuples from the decrypted plaintext
    step = 3
    finaltextone = [decrypted[i:i+step] for i in range(0, len(decrypted), step)]
    finaltexttwo = [(int(finaltextone[int(i)])-100, int(finaltextone[int(i+1)])-100, int(finaltextone[int(i+2)])-100) for i in range(0, len(finaltextone), step)]

    # Reconstruct image from list of pixel RGB tuples
    newim = Image.new("RGB", (int(newwidth), int(newheight)))
    newim.putdata(finaltexttwo)

    # Save the final decrypted image in the same directory
    visual_decrypt_path = os.path.join(image_directory, "visual_decrypt.jpeg")
    newim.save(visual_decrypt_path)
    print("Visual Decryption done......")


# ---------------------
# GUI stuff starts here
# ---------------------

def pass_alert():
    messagebox.showinfo("Password Alert", "Please enter a password.")

def enc_success(imagename):
    messagebox.showinfo("Success", "Encrypted Image: " + imagename)

# image encrypt button event
def image_open():
    global file_path_e

    enc_pass = passg.get()
    if enc_pass == "":
        pass_alert()
    else:
        password = hashlib.sha256(enc_pass.encode('utf-8')).digest()
        filename = filedialog.askopenfilename()
        file_path_e = os.path.dirname(filename)
        encrypt(filename, password)

# image decrypt button event
def cipher_open():
    global file_path_d

    dec_pass = passg.get()
    if dec_pass == "":
        pass_alert()
    else:
        password = hashlib.sha256(dec_pass.encode('utf-8')).digest()
        filename = filedialog.askopenfilename()
        file_path_d = os.path.dirname(filename)
        decrypt(filename, password)

class App:
    def __init__(self, master):
        global passg
        title = "Image Encryption and Decryption"
        author = "Made by Victoria Edwin"

        # Set the background color for the entire GUI
        master.config(bg='darkgreen')

        # Create a frame for layout and set its background color
        frame = Frame(master, bg='darkgreen')
        frame.pack(fill=BOTH, expand=True)
        
        msgtitle = Message(frame, text=title, bg="darkgreen", fg="white")
        msgtitle.config(font=('helvetica', 17, 'bold'), width=200)
        msgtitle.pack(pady=10)

        msgauthor = Message(frame, text=author, bg="darkgreen", fg="white")
        msgauthor.config(font=('helvetica', 10), width=200)
        msgauthor.pack(pady=5)

        passlabel = Label(frame, text="Enter Encrypt/Decrypt Password:", bg="darkgreen", fg="white")
        passlabel.pack(pady=5)

        passg = Entry(frame, show="*", width=20)
        passg.pack(pady=5)

        self.encrypt = Button(frame, text="Encrypt", fg="white", bg="darkorange", font=('helvetica', 12, 'bold'), command=image_open, width=25, height=3, borderwidth=1, relief=RAISED)
        self.encrypt.pack(side=LEFT, padx=5, pady=5)
        self.decrypt = Button(frame, text="Decrypt", fg="white", bg="darkorange", font=('helvetica', 12, 'bold'), command=cipher_open, width=25, height=3, borderwidth=1, relief=RAISED)
        self.decrypt.pack(side=RIGHT, padx=5, pady=5)

# ------------------ MAIN -------------#
root = Tk()
root.wm_title("Image Encryption")
app = App(root)
root.mainloop()
