from fastapi import FastAPI, APIRouter, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from fonction import exif_tools, image_tools, model_tools, ollama_tools
import os
import shutil

# Initialiser l'API FastAPI
app = FastAPI()

# Initialiser le routeur
router = APIRouter()

# Chemin pour stocker les fichiers téléchargés
UPLOAD_FOLDER = "data/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Endpoint pour télécharger et analyser l'image
@router.post("/upload/")
async def upload_image(file: UploadFile, user_description: str = Form(...)):
    try:
        # Enregistrer l'image téléchargée
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Extraire les métadonnées EXIF
        metadata = exif_tools.extract_metadata(file_path)
        if metadata:
            is_retouched, tool_used = exif_tools.is_ai_generated(metadata)
            if is_retouched:
                return JSONResponse(content={
                    "status": "failure",
                    "prediction": "truquée",
                    "explanation": f"L'image semble avoir été modifiée avec un générateur IA, comme {tool_used}.",
                    "decision": "RMA refusé"
                })

        # Préparer et analyser l'image avec EfficientNet
        image = image_tools.load_image(file_path)
        prediction = model_tools.predict_image(image)

        if prediction == "truquée":
            return JSONResponse(content={
                "status": "failure",
                "prediction": prediction,
                "explanation": "L'image contient des modifications détectées.",
                "decision": "RMA refusé"
            })

        # Encoder l'image et analyser avec LLaVA
        image_base64 = image_tools.encode_image_to_base64(file_path)
        ollama_tools.start_ollama_server()

        custom_prompt = f"L'utilisateur a signalé : '{user_description}'. Analysez l'image pour confirmer cette déclaration."
        explanation = ollama_tools.analyze_image_with_llava(image_base64, custom_prompt)
        decision = "RMA accepté" if "accepté" in explanation.lower() else "RMA refusé"

        return JSONResponse(content={
            "status": "success",
            "prediction": prediction,
            "explanation": explanation,
            "decision": decision
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'analyse : {str(e)}")
    finally:
        ollama_tools.stop_ollama_server()

# Ajouter le routeur à l'application FastAPI
app.include_router(router)
