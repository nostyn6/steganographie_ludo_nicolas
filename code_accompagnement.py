from PIL import Image
import tkinter as tk
from tkinter import filedialog, messagebox

def message_to_bin(message):
    # Convertit le message en binaire (8 bits par caractère)
    return ''.join(format(ord(i), '08b') for i in message)

def cacher_message(image_path, message, output_path):
    img = Image.open(image_path)
    binary_msg = message_to_bin(message) + '1111111111111110' # Marqueur de fin
    
    pixels = img.load()
    width, height = img.size
    
    idx = 0
    for y in range(height):
        for x in range(width):
            if idx < len(binary_msg):
                r, g, b = pixels[x, y]
                
                # On modifie le bit de poids faible du canal Rouge
                # (r & ~1) met le dernier bit à 0, puis on ajoute le bit du message
                nouveau_r = (r & ~1) | int(binary_msg[idx])
                
                pixels[x, y] = (nouveau_r, g, b)
                idx += 1
    
    img.save(output_path)
    print(f"Message caché dans {output_path}")

def extraire_message(image_path):
    img = Image.open(image_path)
    pixels = img.load()
    width, height = img.size
    
    bits_extraits = ""
    message_final = ""
    marqueur_fin = '1111111111111110'
    
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            
            # On récupère le bit de poids faible (LSB) avec l'opérateur ET
            bits_extraits += str(r & 1)
            
            # On vérifie si on a trouvé le marqueur de fin
            if bits_extraits.endswith(marqueur_fin):
                # On retire le marqueur pour ne garder que les données
                bits_utiles = bits_extraits[:-len(marqueur_fin)]
                
                # On regroupe par 8 bits pour reformer les caractères
                for i in range(0, len(bits_utiles), 8):
                    octet = bits_utiles[i:i+8]
                    message_final += chr(int(octet, 2))
                
                return message_final
    
    return "Aucun marqueur de fin trouvé."



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


def selectionner_image_cacher():
    chemin = filedialog.askopenfilename(
        title="Sélectionner une image",
        filetypes=[("Images PNG", "*.png")]
    )
    entry_image_cacher.delete(0, tk.END)
    entry_image_cacher.insert(0, chemin)

def selectionner_image_extraire():
    chemin = filedialog.askopenfilename(
        title="Sélectionner une image",
        filetypes=[("Images PNG", "*.png")]
    )
    entry_image_extraire.delete(0, tk.END)
    entry_image_extraire.insert(0, chemin)

def cacher():
    image_source = entry_image_cacher.get()
    message = entry_message.get()

    if not image_source or not message:
        messagebox.showerror("Erreur", "Image ou message manquant")
        return

    image_sortie = "image_codee.png"

    try:
        cacher_message(image_source, message, image_sortie)
        messagebox.showinfo("Succès", f"Image créée : {image_sortie}")
    except Exception as e:
        messagebox.showerror("Erreur", str(e))

def extraire():
    image_source = entry_image_extraire.get()

    if not image_source:
        messagebox.showerror("Erreur", "Aucune image sélectionnée")
        return

    try:
        message = extraire_message(image_source)

        if message:
            label_resultat.config(text="Message trouvé : " + message)
        else:
            label_resultat.config(text="Aucun message caché")

    except Exception as e:
        messagebox.showerror("Erreur", str(e))

root = tk.Tk()
root.title("Stéganographie - Cacher / Extraire")

frame_cacher = tk.LabelFrame(root, text="Cacher un message", padx=10, pady=10)
frame_cacher.pack(padx=10, pady=10, fill="x")

tk.Label(frame_cacher, text="Image source :").pack()
entry_image_cacher = tk.Entry(frame_cacher, width=50)
entry_image_cacher.pack()
tk.Button(frame_cacher, text="Parcourir", command=selectionner_image_cacher).pack(pady=5)

tk.Label(frame_cacher, text="Message :").pack()
entry_message = tk.Entry(frame_cacher, width=50)
entry_message.pack()

tk.Button(frame_cacher, text="Cacher le message", command=cacher).pack(pady=10)

frame_extraire = tk.LabelFrame(root, text="Extraire un message", padx=10, pady=10)
frame_extraire.pack(padx=10, pady=10, fill="x")

tk.Label(frame_extraire, text="Image :").pack()
entry_image_extraire = tk.Entry(frame_extraire, width=50)
entry_image_extraire.pack()
tk.Button(frame_extraire, text="Parcourir", command=selectionner_image_extraire).pack(pady=5)

tk.Button(frame_extraire, text="Extraire le message", command=extraire).pack(pady=10)

label_resultat = tk.Label(frame_extraire, text="")
label_resultat.pack()

root.mainloop()

def image_difference(image1, image2, image_difference_output):
    img1 = Image.open(image1)
    img2 = Image.open(image2)

    if img1.size != img2.size:
        print("Les images n'ont pas la même taille. Opération annulée.")
        return

    width, height = img1.size

    img_diff = Image.new("RGB", (width, height))

    pixels1 = img1.load()
    pixels2 = img2.load()
    pixels_diff = img_diff.load()

    for y in range(height):
        for x in range(width):
            if pixels1[x, y] == pixels2[x, y]:
                pixels_diff[x, y] = (255, 255, 255)
            else:
                pixels_diff[x, y] = (255, 0, 0)

    img_diff.save(image_difference_output)

def afficher_dernier_pixel_rouge(image_difference_output):
    img = Image.open(image_difference_output).convert("RGB")
    width, height = img.size
    pixels = img.load()

    for y in range(height - 1, -1, -1):
        for x in range(width - 1, -1, -1):
            if pixels[x, y] == (255, 0, 0):
                r, g, b = pixels[x, y]
                print("Valeur du dernier pixel rouge :", r, g, b)
                return
            
    print("Aucun pixel rouge trouvé.")

# image_difference("image2.png", "image_codee.png", "difference.png")
afficher_dernier_pixel_rouge("difference.png")