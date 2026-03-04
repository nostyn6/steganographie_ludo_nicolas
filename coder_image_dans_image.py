from PIL import Image
import tkinter as tk
from tkinter import filedialog, messagebox
import random

def generer_points_aleatoires(largeur, hauteur, nb_bits, graine):
    random.seed(graine)
    indices_possibles = list(range(largeur * hauteur))
    indices_choisis = random.sample(indices_possibles, nb_bits)
    points = [(i % largeur, i // largeur) for i in indices_choisis]
    return points

def int_to_bin16(n):
    return format(n, '016b')

def bin16_to_int(b):
    return int(b, 2)

def cacher_image(image_porteur_path, image_a_cacher_path, output_path, graine):
    porteur = Image.open(image_porteur_path).convert("RGB")
    cacher = Image.open(image_a_cacher_path).convert("1")  # B/W
    width_p, height_p = porteur.size
    width_c, height_c = cacher.size

    if width_c > 255 or height_c > 255:
        print("Image cachée trop grande (max 255x255)")
        return

    nb_bits_image = width_c * height_c
    total_bits = 16 + nb_bits_image 
    if total_bits > width_p * height_p:
        print("Image porteuse trop petite pour stocker l'image")
        return

    pixels_p = porteur.load()
    pixels_c = cacher.load()

    points = generer_points_aleatoires(width_p, height_p, total_bits, graine)

    taille_bits = int_to_bin16((width_c << 8) + height_c)
    for idx in range(16):
        x, y = points[idx]
        r, g, b = pixels_p[x, y]
        pixels_p[x, y] = ((r & ~1) | int(taille_bits[idx]), g, b)

    idx_bit = 16
    for y in range(height_c):
        for x in range(width_c):
            bit = 0 if pixels_c[x, y] == 0 else 1
            px, py = points[idx_bit]
            r, g, b = pixels_p[px, py]
            pixels_p[px, py] = ((r & ~1) | bit, g, b)
            idx_bit += 1

    porteur.save(output_path)
    print(f"Image cachée dans {output_path}")

def extraire_image(image_codee_path, graine):
    img = Image.open(image_codee_path).convert("RGB")
    width_p, height_p = img.size
    pixels_p = img.load()

    points = generer_points_aleatoires(width_p, height_p, width_p * height_p, graine)
    taille_bits = ""
    for i in range(16):
        x, y = points[i]
        r, g, b = pixels_p[x, y]
        taille_bits += str(r & 1)

    taille = bin16_to_int(taille_bits)
    width_c = (taille >> 8) & 0xFF
    height_c = taille & 0xFF

    cacher = Image.new("1", (width_c, height_c))
    pixels_c = cacher.load()

    idx_bit = 16
    for y in range(height_c):
        for x in range(width_c):
            px, py = points[idx_bit]
            r, g, b = pixels_p[px, py]
            pixels_c[x, y] = 255 if r & 1 else 0
            idx_bit += 1

    return cacher

cacher_image("image1.png", "logoMNS_NB.png", "image_code.png", graine="monsecret")
logo_extrait = extraire_image("image_code.png", graine="monsecret")
logo_extrait.show()