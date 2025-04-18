/* scripts.js
 *  - Upload : résultat fixe après POST (page reload).
 *  - Webcam : capture régulière et prédiction live.
 */

const radioUpload     = document.getElementById('radioUpload');
const radioWebcam     = document.getElementById('radioWebcam');
const video           = document.getElementById('video');
const resultImg       = document.getElementById('predictedImg');  // <img> pour image annotée

let stream            = null;
let captureIntervalId = null;
const CAPTURE_DELAY   = 1000;  // ms
const MIN_IMAGE_SIZE  = 1000;  // taille minimale en base64

/* ----------- Webcam helpers ------------------ */
async function startWebcam() {
  if (stream) return;

  try {
    stream = await navigator.mediaDevices.getUserMedia({ video: true });
    video.srcObject = stream;
    await video.play();
    captureIntervalId = setInterval(captureFrameAndPredict, CAPTURE_DELAY);
  } catch (err) {
    console.error('Webcam error:', err);
    alert('Impossible d’accéder à la webcam.');
    radioUpload.checked = true;
    stopWebcam();
  }
}

function stopWebcam() {
  if (captureIntervalId) clearInterval(captureIntervalId);
  if (stream) {
    stream.getTracks().forEach(t => t.stop());
    stream = null;
  }
}

/* ----------- Capture et envoi des frames ------------ */
async function captureFrameAndPredict() {
  if (!video.videoWidth || !video.videoHeight) return;

  const canvas = document.createElement('canvas');
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  canvas.getContext('2d').drawImage(video, 0, 0);
  const dataURL = canvas.toDataURL('image/png');

  if (!dataURL.startsWith('data:image/png;base64,')) return;
  const base64Data = dataURL.split(',')[1];
  if (base64Data.length < MIN_IMAGE_SIZE) return;

  try {
    const res = await fetch('/predict_webcam_frame', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ image: dataURL })
    });

    const data = await res.json();

    if (data.image) {
      resultImg.src = data.image;  // Met à jour l'image annotée
    } else if (data.error) {
      console.warn('Erreur serveur :', data.error);
    }
  } catch (err) {
    console.error('Prediction error:', err);
    stopWebcam();
    alert("Erreur de prédiction. La webcam a été arrêtée.");
  }
}

/* ----------- Changement de source ------------ */
function handleSourceChange() {
  if (radioWebcam.checked) {
    startWebcam();
    resultImg.src = ""; // reset image affichée
  } else {
    stopWebcam();
  }
}

radioUpload.addEventListener('change', handleSourceChange);
radioWebcam.addEventListener('change', handleSourceChange);
window.addEventListener('beforeunload', stopWebcam);

// Auto-start si webcam sélectionnée
if (radioWebcam.checked) startWebcam();
