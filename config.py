import os

# Définir les chemins
MODEL_PATH = "models/saved/efficientnet_b3.pth"
UPLOAD_FOLDER = "data/uploads"
EXIF_TOOL_PATH = r'"C:\\Program Files\\exiftool-12.97_64\\exiftool.exe"'

# Créer le dossier de téléchargements si nécessaire
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
