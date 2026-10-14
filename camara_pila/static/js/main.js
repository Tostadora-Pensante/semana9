"use strict";

const app = document.querySelector("#photoApp");
const video = document.querySelector("#camera");
const canvas = document.querySelector("#canvas");
const statusBox = document.querySelector("#status");
const gallery = document.querySelector("#gallery");
const count = document.querySelector("#count");
const emptyStack = document.querySelector("#emptyStack");

const startButton = document.querySelector("#startCamera");
const captureButton = document.querySelector("#capturePhoto");
const stopButton = document.querySelector("#stopCamera");
const popButton = document.querySelector("#popPhoto");

let stream = null;
let busy = false;
let starting = false;
let photoCount = 0;

function showMessage(message, type = "info") {
    statusBox.className = `alert alert-${type}`;
    statusBox.textContent = message;
}

function updateButtons() {
    startButton.disabled = starting || stream !== null;
    captureButton.disabled = busy || stream === null;
    stopButton.disabled = busy || stream === null;
    popButton.disabled = busy || photoCount === 0;
}

async function apiRequest(url, options = {}) {
    const response = await fetch(url, {
        ...options,
        headers: {
            "X-Photo-App": "camera-stack",
            ...options.headers,
        },
        cache: "no-store",
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.error || "No se pudo completar la operación.");
    }

    return data;
}

async function refreshStack() {
    const data = await apiRequest(app.dataset.listUrl);

    photoCount = data.count;
    count.textContent = String(photoCount);
    emptyStack.hidden = photoCount > 0;
    gallery.replaceChildren();

    data.photos.forEach((photo, index) => {
        const column = document.createElement("div");
        column.className = "col-12 col-sm-6";

        const figure = document.createElement("figure");
        figure.className = "mb-0";

        const image = document.createElement("img");
        image.src = photo.url;
        image.alt = `Fotografía en la posición ${index + 1} de la pila`;
        image.className = "img-fluid rounded border";
        image.loading = "lazy";

        const caption = document.createElement("figcaption");
        caption.className = "small text-secondary mt-1";
        caption.textContent = index === 0
            ? "Cima: última fotografía capturada"
            : `Posición ${index + 1} desde la cima`;

        figure.append(image, caption);
        column.append(figure);
        gallery.append(column);
    });

    updateButtons();
}

function stopCamera() {
    if (stream) {
        stream.getTracks().forEach((track) => track.stop());
    }

    stream = null;
    video.srcObject = null;
    updateButtons();
}

startButton.addEventListener("click", async () => {
    starting = true;
    updateButtons();
    showMessage("Esperando permiso para usar la cámara...");

    try {
        if (!navigator.mediaDevices?.getUserMedia) {
            throw new Error("Abre la aplicación en localhost o mediante HTTPS.");
        }

        stream = await navigator.mediaDevices.getUserMedia({
            video: {
                width: { ideal: 1280 },
                height: { ideal: 720 },
            },
            audio: false,
        });

        video.srcObject = stream;
        await video.play();

        showMessage("Cámara activa. Ya puedes capturar fotografías.", "success");
    } catch (error) {
        stopCamera();

        const messages = {
            NotAllowedError: "Permiso denegado. Autoriza la cámara en el navegador.",
            NotFoundError: "No se encontró una cámara disponible.",
            NotReadableError: "No se pudo abrir la cámara. Puede estar ocupada.",
        };

        showMessage(messages[error.name] || error.message, "danger");
    } finally {
        starting = false;
        updateButtons();
    }
});

stopButton.addEventListener("click", () => {
    stopCamera();
    showMessage("Cámara apagada.");
});

async function performOperation(operation) {
    if (busy) return;

    busy = true;
    updateButtons();

    try {
        const result = await operation();
        showMessage(result.message, "success");

        try {
            await refreshStack();
        } catch {
            showMessage(
                `${result.message} No se pudo actualizar la galería; recarga la página.`,
                "warning"
            );
        }
    } catch (error) {
        showMessage(error.message, "danger");
    } finally {
        busy = false;
        updateButtons();
    }
}

captureButton.addEventListener("click", () => {
    performOperation(async () => {
        if (!stream || video.readyState < 2 || !video.videoWidth) {
            throw new Error("Espera a que la cámara muestre una imagen.");
        }

        showMessage("Capturando y guardando fotografía...");

        const scale = Math.min(
            1,
            1280 / Math.max(video.videoWidth, video.videoHeight)
        );

        canvas.width = Math.round(video.videoWidth * scale);
        canvas.height = Math.round(video.videoHeight * scale);

        const context = canvas.getContext("2d");
        if (!context) {
            throw new Error("No se pudo preparar la captura.");
        }

        context.drawImage(video, 0, 0, canvas.width, canvas.height);

        const blob = await new Promise((resolve, reject) => {
            canvas.toBlob((result) => {
                if (result) resolve(result);
                else reject(new Error("No se pudo generar la fotografía."));
            }, "image/jpeg", 0.85);
        });

        const formData = new FormData();
        formData.append("photo", blob, "capture.jpg");

        return apiRequest(app.dataset.captureUrl, {
            method: "POST",
            body: formData,
        });
    });
});

popButton.addEventListener("click", () => {
    if (!window.confirm("¿Eliminar la fotografía de la cima de la pila?")) {
        return;
    }

    performOperation(() =>
        apiRequest(app.dataset.popUrl, { method: "POST" })
    );
});

window.addEventListener("pagehide", stopCamera);

refreshStack().catch((error) => {
    showMessage(error.message, "danger");
});