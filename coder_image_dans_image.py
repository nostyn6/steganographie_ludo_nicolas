from PIL import Image
import tkinter as tk
from tkinter import filedialog, messagebox
import random

def generer_points_aleatoires(largeur, hauteur, nb_bits, graine):
    # On initialise le générateur avec la clé (la graine)
    random.seed(graine)
    
    # Création de la liste de tous les indices possibles (linéaires)
    indices_possibles = list(range(largeur * hauteur))
    
    # On pioche nb_bits indices sans remise (pour ne pas modifier deux fois le même pixel)
    indices_choisis = random.sample(indices_possibles, nb_bits)
    
    # Conversion des indices linéaires en coordonnées (x, y)
    points = []
    for i in indices_choisis:
        x = i % largeur
        y = i // largeur
        points.append((x, y))
        
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

root = tk.Tk()
root.title("Stéganographie : cacher une image dans une image")

frame_cacher = tk.LabelFrame(root, text="Cacher une image", padx=10, pady=10)
frame_cacher.pack(padx=10, pady=10, fill="x")

tk.Label(frame_cacher, text="Image porteuse :").pack()
entry_porteur = tk.Entry(frame_cacher, width=50)
entry_porteur.pack()
def selectionner_porteur():
    chemin = filedialog.askopenfilename(title="Sélectionner image porteuse", filetypes=[("Images PNG", "*.png")])
    entry_porteur.delete(0, tk.END)
    entry_porteur.insert(0, chemin)
tk.Button(frame_cacher, text="Parcourir", command=selectionner_porteur).pack(pady=5)

tk.Label(frame_cacher, text="Image à cacher (B/W) :").pack()
entry_cacher = tk.Entry(frame_cacher, width=50)
entry_cacher.pack()
def selectionner_cacher():
    chemin = filedialog.askopenfilename(title="Sélectionner image à cacher", filetypes=[("Images PNG", "*.png")])
    entry_cacher.delete(0, tk.END)
    entry_cacher.insert(0, chemin)
tk.Button(frame_cacher, text="Parcourir", command=selectionner_cacher).pack(pady=5)

tk.Label(frame_cacher, text="Graine (mot de passe) :").pack()
entry_graine = tk.Entry(frame_cacher, width=50)
entry_graine.pack()

def cacher_action():
    porteur = entry_porteur.get()
    cacher_img = entry_cacher.get()
    graine = entry_graine.get()
    if not porteur or not cacher_img or not graine:
        messagebox.showerror("Erreur", "Veuillez remplir tous les champs")
        return
    cacher_image(porteur, cacher_img, "image_codee.png", graine)
tk.Button(frame_cacher, text="Cacher l'image", command=cacher_action).pack(pady=10)

frame_extraire = tk.LabelFrame(root, text="Extraire l'image", padx=10, pady=10)
frame_extraire.pack(padx=10, pady=10, fill="x")

tk.Label(frame_extraire, text="Image codée :").pack()
entry_codee = tk.Entry(frame_extraire, width=50)
entry_codee.pack()
def selectionner_codee():
    chemin = filedialog.askopenfilename(title="Sélectionner image codée", filetypes=[("Images PNG", "*.png")])
    entry_codee.delete(0, tk.END)
    entry_codee.insert(0, chemin)
tk.Button(frame_extraire, text="Parcourir", command=selectionner_codee).pack(pady=5)

tk.Label(frame_extraire, text="Graine (mot de passe) :").pack()
entry_graine_extraire = tk.Entry(frame_extraire, width=50)
entry_graine_extraire.pack()

def extraire_action():
    codee = entry_codee.get()
    graine = entry_graine_extraire.get()
    if not codee or not graine:
        messagebox.showerror("Erreur", "Veuillez remplir tous les champs")
        return
    image_extrait = extraire_image(codee, graine)
    image_extrait.show()
tk.Button(frame_extraire, text="Extraire l'image", command=extraire_action).pack(pady=10)

root.mainloop()