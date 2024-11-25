# import subprocess
# import requests
# import base64
# import time
# import shutil
# import json
# import sys
# import os
# from pathlib import Path
# from fastapi import APIRouter, UploadFile, Form, HTTPException
# from fastapi.responses import JSONResponse
# from PIL import Image
# import torch
# from torchvision import models, transforms

# # Initialiser le routeur
# router = APIRouter()

# # Charger le modèle EfficientNet
# MODEL_PATH = "models/saved/efficientnet_b3.pth"
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# model = models.efficientnet_b3(weights=None)
# in_features = model.classifier[1].in_features
# model.classifier = torch.nn.Sequential(
#     torch.nn.Linear(in_features, 1)
# )
# model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
# model = model.to(device)
# model.eval()

# # Définir les transformations des images
# transform = transforms.Compose([
#     transforms.Resize((256, 256)),
#     transforms.ToTensor(),
# ])

# # Chemin pour stocker les fichiers téléchargés
# UPLOAD_FOLDER = "data/uploads"
# Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)

# # Fonction pour encoder une image en base64
# def encode_image_to_base64(image_path):
#     try:
#         with open(image_path, "rb") as image_file:
#             return base64.b64encode(image_file.read()).decode("utf-8")
#     except FileNotFoundError:
#         print(f"Erreur : Le fichier '{image_path}' n'existe pas.")
#         raise HTTPException(status_code=400, detail=f"Le fichier '{image_path}' n'existe pas.")

# # Vérifie si le serveur Ollama est déjà en marche
# def is_ollama_server_running():
#     try:
#         response = requests.get("http://localhost:11434/api/health")
#         return response.status_code == 200
#     except requests.ConnectionError:
#         return False

# # Démarre le serveur Ollama uniquement s'il n'est pas déjà en marche
# # def start_ollama_server():
# #     if is_ollama_server_running():
# #         print("Le serveur Ollama est déjà en cours d'exécution.")
# #     else:
# #         try:
# #             subprocess.Popen(["ollama", "run", "llava"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
# #             print("Démarrage du serveur Ollama avec LLaVA...")
# #             time.sleep(5)
# #         except FileNotFoundError:
# #             raise HTTPException(status_code=500, detail="Erreur : Ollama n'est pas installé ou n'est pas dans le PATH.")
        

# def start_ollama_server():
#     if is_ollama_server_running():
#         print("Le serveur Ollama est déjà en cours d'exécution.")
#     else:
#         try:
#             subprocess.Popen(
#                 ["ollama", "run", "llava:latest"], 
#                 stdout=subprocess.DEVNULL, 
#                 stderr=subprocess.DEVNULL
#             )
#             print("Démarrage du serveur Ollama avec llava:latest...")
#             time.sleep(5)  # Laisser le temps au serveur de démarrer
#         except FileNotFoundError:
#             raise HTTPException(status_code=500, detail="Erreur : Ollama n'est pas installé ou n'est pas dans le PATH.")


# # Arrête le serveur Ollama après la requête
# def stop_ollama_server():
#     try:
#         subprocess.Popen(["taskkill", "/F", "/IM", "ollama.exe"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#         print("Serveur Ollama arrêté.")
#     except Exception as e:
#         print(f"Erreur lors de l'arrêt du serveur Ollama : {e}")

# # Fonction pour envoyer une requête à Ollama et analyser l'image
# def analyze_image_with_llava(image_base64, custom_prompt):
#     url = "http://localhost:11434/api/generate"
#     payload = {
#         "model": "llava",
#         "prompt": custom_prompt,
#         "temperature": 0.2,
#         "images": [image_base64]
#     }

#     try:
#         response = requests.post(url, json=payload)
#         response_lines = response.text.strip().split('\n')
#         full_response = ''.join(json.loads(line)['response'] for line in response_lines if 'response' in json.loads(line))
#         return full_response
#     except Exception as e:
#         return f"Erreur : {e}"

# @router.post("/upload/")
# async def upload_image(file: UploadFile, user_description: str = Form(...)):

#     """
#     Endpoint pour télécharger une image, analyser son contenu et évaluer le RMA.
#     """
#     try:
#         # Enregistrer l'image téléchargée
#         file_path = f"{UPLOAD_FOLDER}/{file.filename}"
#         with open(file_path, "wb") as buffer:
#             shutil.copyfileobj(file.file, buffer)

#         # Préparer l'image pour le modèle EfficientNet
#         image = Image.open(file_path).convert("RGB")
#         input_tensor = transform(image).unsqueeze(0).to(device)

#         # Effectuer la prédiction avec EfficientNet
#         with torch.no_grad():
#             output = model(input_tensor).item()
#         prediction = "truquée" if output > 0.5 else "authentique"

#         # Vérifier si l'image est retouchée (simple simulation ici, à personnaliser avec vos critères)
#         if prediction == "truquée":
#             explanation = "L'image contient des modifications ou des manipulations numériques détectées."
#             return JSONResponse(content={
#                 "status": "failure",
#                 "prediction": prediction,
#                 "explanation": explanation,
#                 "decision": "RMA refusé"
#             })

#         # Encoder l'image en base64
#         image_base64 = encode_image_to_base64(file_path)

#         # Démarrer le serveur Ollama pour LLaVA
#         start_ollama_server()

#         # Construire le prompt pour LLaVA
#         custom_prompt = (
#             f"L'utilisateur a signalé : '{user_description}'. "
#             "Analysez l'image pour confirmer cette déclaration et concluez par un RMA accepté ou refusé."
#         )
#         explanation = analyze_image_with_llava(image_base64, custom_prompt)

#         # Vérifier si aucune explication n'a été générée
#         if not explanation.strip():
#             explanation = "Aucune explication n'a pu être générée pour cette image."

#         decision = "RMA accepté" if "accepté" in explanation.lower() else "RMA refusé"

#         # Retourner les résultats
#         return JSONResponse(content={
#             "status": "success",
#             "prediction": prediction,
#             "explanation": explanation,
#             "decision": decision
#         })

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Erreur lors de l'analyse : {str(e)}")
#     finally:
#         stop_ollama_server()


import subprocess
import requests
import base64
import time
import shutil
import json
import sys
import os
from pathlib import Path
from fastapi import APIRouter, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from PIL import Image
import torch
from torchvision import models, transforms

# Initialiser le routeur
router = APIRouter()

# Charger le modèle EfficientNet
MODEL_PATH = "models/saved/efficientnet_b3.pth"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = models.efficientnet_b3(weights=None)
in_features = model.classifier[1].in_features
model.classifier = torch.nn.Sequential(
    torch.nn.Linear(in_features, 1)
)
model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
model = model.to(device)
model.eval()

# Définir les transformations des images
transform = transforms.Compose([
    transforms.Resize((256, 256)),
    transforms.ToTensor(),
])

# Chemin pour stocker les fichiers téléchargés
UPLOAD_FOLDER = "data/uploads"
Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)

# Fonction pour encoder une image en base64
# def encode_image_to_base64(image_path):
#     try:
#         with open(image_path, "rb") as image_file:
#             return base64.b64encode(image_file.read()).decode("utf-8")
#     except FileNotFoundError:
#         print(f"Erreur : Le fichier '{image_path}' n'existe pas.")
#         raise HTTPException(status_code=400, detail=f"Le fichier '{image_path}' n'existe pas.")

def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode("utf-8")
            print(f"DEBUG: Image encodée en base64 (extrait) : {encoded[:100]}...")  # Affiche les 100 premiers caractères
            return encoded
    except FileNotFoundError:
        print(f"Erreur : Le fichier '{image_path}' n'existe pas.")
        raise HTTPException(status_code=400, detail=f"Le fichier '{image_path}' n'existe pas.")


# Vérifie si le serveur Ollama est déjà en marche
def is_ollama_server_running():
    try:
        response = requests.get("http://localhost:11434/api/health")
        return response.status_code == 200
    except requests.ConnectionError:
        return False

# # Démarre le serveur Ollama uniquement s'il n'est pas déjà en marche
# def start_ollama_server():
#     if is_ollama_server_running():
#         print("Le serveur Ollama est déjà en cours d'exécution.")
#     else:
#         try:
#             subprocess.Popen(["ollama", "run", "llava"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
#             print("Démarrage du serveur Ollama avec LLaVA...")
#             time.sleep(5)
#         except FileNotFoundError:
#             raise HTTPException(status_code=500, detail="Erreur : Ollama n'est pas installé ou n'est pas dans le PATH.")

def start_ollama_server():
    if is_ollama_server_running():
        print("Le serveur Ollama est déjà en cours d'exécution.")
    else:
        try:
            subprocess.Popen(
                ["ollama", "run", "llava:quantized"], 
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL
            )
            print("Démarrage du serveur Ollama avec LLaVA (modèle quantifié)...")
            time.sleep(10)  # Laissez le serveur démarrer
        except FileNotFoundError:
            raise HTTPException(status_code=500, detail="Erreur : Ollama n'est pas installé ou n'est pas dans le PATH.")



# Arrête le serveur Ollama après la requête
def stop_ollama_server():
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "ollama.exe"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Serveur Ollama arrêté.")
    except Exception as e:
        print(f"Erreur lors de l'arrêt du serveur Ollama : {e}")

# def start_ollama_server():
#     if is_ollama_server_running():
#         print("Le serveur Ollama est déjà en cours d'exécution.")
#     else:
#         try:
#             subprocess.Popen(
#                 ["ollama", "run", "llava:latest"], 
#                 stdout=subprocess.DEVNULL, 
#                 stderr=subprocess.DEVNULL
#             )
#             print("Démarrage du serveur Ollama avec llava:latest...")
#             time.sleep(5)  # Laisser le temps au serveur de démarrer
#         except FileNotFoundError:
#             raise HTTPException(status_code=500, detail="Erreur : Ollama n'est pas installé ou n'est pas dans le PATH.")

# def stop_ollama_server():
#     try:
#         if os.name == 'nt':  # Pour Windows
#             subprocess.Popen(["taskkill", "/F", "/IM", "ollama.exe"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#         else:  # Pour Linux/MacOS
#             subprocess.Popen(["pkill", "-f", "ollama"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#         print("Serveur Ollama arrêté.")
#     except Exception as e:
#         print(f"Erreur lors de l'arrêt du serveur Ollama : {e}")


# Fonction pour envoyer une requête à Ollama et analyser l'image
# def analyze_image_with_llava(image_base64, custom_prompt):
#     url = "http://localhost:11434/api/generate"
#     payload = {
#         "model": "llava:latest",
#         "prompt": custom_prompt,
#         "temperature": 0.2,
#         "images": [image_base64]
#     }

#     try:
#         response = requests.post(url, json=payload)
#         response_lines = response.text.strip().split('\n')
#         full_response = ''.join(json.loads(line)['response'] for line in response_lines if 'response' in json.loads(line))
#         return full_response
#     except Exception as e:
#         return f"Erreur : {e}"


def analyze_image_with_llava(image_base64, custom_prompt):
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "llava",
        "prompt": custom_prompt,
        "temperature": 0.2,
        "images": [image_base64]
    }

    try:
        print(f"DEBUG: Payload envoyé à LLaVA : {json.dumps(payload)}")
        response = requests.post(url, json=payload, timeout=30)
        print(f"DEBUG: Statut de la réponse LLaVA : {response.status_code}")
        print(f"DEBUG: Réponse brute de LLaVA : {response.text}")

        if not response.text.strip():
            return "LLaVA n'a pas pu fournir une réponse pour cette image."

        # Traiter la réponse ligne par ligne si nécessaire
        response_lines = response.text.strip().split('\n')
        full_response = ''.join(json.loads(line).get('response', '') for line in response_lines if line.strip())
        return full_response
    except Exception as e:
        print(f"Erreur lors de l'appel à LLaVA : {e}")
        return f"Erreur : {e}"


@router.post("/upload/")
async def upload_image(file: UploadFile, user_description: str = Form(...)):
    """
    Endpoint pour télécharger une image, analyser son contenu et évaluer le RMA.
    """
    try:
        # Enregistrer l'image téléchargée
        file_path = f"{UPLOAD_FOLDER}/{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Préparer l'image pour le modèle EfficientNet
        image = Image.open(file_path).convert("RGB")
        input_tensor = transform(image).unsqueeze(0).to(device)

        # Effectuer la prédiction avec EfficientNet
        with torch.no_grad():
            output = model(input_tensor).item()
        prediction = "truquée" if output > 0.5 else "authentique"

        # Vérifier si l'image est retouchée (simple simulation ici, à personnaliser avec vos critères)
        if prediction == "truquée":
            explanation = "L'image contient des modifications ou des manipulations numériques détectées."
            return JSONResponse(content={
                "status": "failure",
                "prediction": prediction,
                "explanation": explanation,
                "decision": "RMA refusé"
            })

        # Encoder l'image en base64
        image_base64 = encode_image_to_base64(file_path)

        # Démarrer le serveur Ollama pour LLaVA
        start_ollama_server()

        # Construire le prompt pour LLaVA
        custom_prompt = (
            f"L'utilisateur a signalé : '{user_description}'. "
            "Analysez l'image pour confirmer cette déclaration si c'est vrai et concluez par un RMA accepté ou refusé."
        )
        print(f"DEBUG: Prompt envoyé à LLaVA : {custom_prompt}")
        explanation = analyze_image_with_llava(image_base64, custom_prompt)
        print(f"DEBUG : Réponse générée par LLaVA : {explanation}")

        # Vérifier si aucune explication n'a été générée
        if not explanation.strip():
            explanation = "Aucune explication n'a pu être générée pour cette image."

        decision = "RMA accepté" if "accepté" in explanation.lower() else "RMA refusé"

        print("DEBUG: JSON Response:", {
            "status": "success",
            "prediction": prediction,
            "explanation": explanation,
            "decision": decision
        })


        # Retourner les résultats
        return JSONResponse(content={
            "status": "success",
            "prediction": prediction,
            "explanation": explanation,
            "decision": decision
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'analyse : {str(e)}")
    finally:
        stop_ollama_server()
