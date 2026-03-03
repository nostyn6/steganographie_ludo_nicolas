from PIL import Image

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

# Exemple d'utilisation
cacher_message("image_originale.png", "Secret NSI 2026", "image_codee.png")




from PIL import Image

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

# Exemple d'utilisation :
print(extraire_message("image_codee.png"))



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