import base64
import os
import tempfile

try:
    import face_recognition
except ImportError:  # pragma: no cover - depende do ambiente de deploy
    face_recognition = None


def validar_face(foto_referencia, foto_base64):

    if face_recognition is None:
        return False

    if "," in foto_base64:
        imagem_base64 = foto_base64.split(",", 1)[1]
    else:
        imagem_base64 = foto_base64

    imagem_bytes = base64.b64decode(imagem_base64)

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp:
            temp.write(imagem_bytes)
            temp.flush()
            temp_path = temp.name

        imagem_registro = face_recognition.load_image_file(temp_path)
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

    imagem_cadastro = face_recognition.load_image_file(foto_referencia.path)

    enc_cadastro = face_recognition.face_encodings(imagem_cadastro)

    enc_registro = face_recognition.face_encodings(imagem_registro)

    if not enc_cadastro or not enc_registro:
        return False

    resultado = face_recognition.compare_faces(
        [enc_cadastro[0]], enc_registro[0], tolerance=0.50
    )

    return resultado[0]
