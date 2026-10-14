from io import BytesIO

from flask import (
    Blueprint,
    Response,
    abort,
    current_app,
    jsonify,
    render_template,
    request,
    url_for,
)
from PIL import Image, UnidentifiedImageError

from stack import PhotoStack

main_bp = Blueprint("main", __name__)


def get_stack() -> PhotoStack:
    return current_app.extensions["photo_stack"]


def normalize_image(content: bytes) -> bytes:
    """Decodifica la captura y genera un JPEG sin metadatos originales."""
    with Image.open(BytesIO(content)) as image:
        if image.format not in {"JPEG", "PNG"}:
            raise ValueError("Solo se aceptan imágenes JPEG o PNG.")

        width, height = image.size

        if width * height > 4_000_000:
            raise ValueError("La imagen no puede superar 4 millones de píxeles.")

        image.load()
        converted = image.convert("RGB")
        converted.thumbnail((1280, 1280))

        output = BytesIO()
        converted.save(output, format="JPEG", quality=85)

        return output.getvalue()


@main_bp.before_request
def protect_write_requests():
    # Protección básica para esta demostración local:
    # las escrituras deben proceder de nuestro cliente JavaScript.
    # No habilitar CORS permisivo para estas rutas.
    if request.method == "POST":
        if request.headers.get("X-Photo-App") != "camera-stack":
            return jsonify(error="Solicitud no permitida."), 403


@main_bp.get("/")
def index():
    return render_template("index.html")


@main_bp.get("/api/photos")
def list_photos():
    photos = get_stack().snapshot()

    return jsonify(
        count=len(photos),
        photos=[
            {
                "id": photo.id,
                "url": url_for("main.photo_image", photo_id=photo.id),
            }
            for photo in photos
        ],
    )


@main_bp.post("/api/photos")
def capture_photo():
    uploaded = request.files.get("photo")

    if uploaded is None:
        return jsonify(error="No se recibió una fotografía."), 400

    try:
        content = normalize_image(uploaded.read())
    except (
        UnidentifiedImageError,
        Image.DecompressionBombError,
        OSError,
        ValueError,
    ):
        return jsonify(error="La imagen es inválida o supera los límites."), 400

    try:
        photo = get_stack().push(content)
    except OverflowError as error:
        return jsonify(error=str(error)), 409

    return jsonify(
        message="Fotografía capturada y apilada.",
        id=photo.id,
    ), 201


@main_bp.post("/api/photos/pop")
def pop_photo():
    try:
        photo = get_stack().pop()
    except IndexError as error:
        return jsonify(error=str(error)), 409

    return jsonify(
        message="Se retiró la fotografía de la cima.",
        id=photo.id,
    )


@main_bp.get("/photos/<photo_id>")
def photo_image(photo_id: str):
    photo = get_stack().find(photo_id)

    if photo is None:
        abort(404)

    return Response(
        photo.content,
        mimetype="image/jpeg",
        headers={"Cache-Control": "no-store"},
    )