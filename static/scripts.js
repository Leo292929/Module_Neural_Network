/* scripts.js
 *  - Upload : résultat fixe après POST (page reload).
 *  - Webcam : capture régulière et prédiction live.
 */

const radioUpload     = document.getElementById('radioUpload');
const radioWebcam     = document.getElementById('radioWebcam');
const video           = document.getElementById('video');
const predictionText  = document.getElementById('predictionText');

let stream            = null;          // flux webcam
let captureIntervalId = null;          // setInterval id
const CAPTURE_DELAY   = 1000;          // ms entre 2 frames
const MIN_IMAGE_SIZE  = 1000;          // octets minimum pour éviter les frames vides

/* ----------- Webcam helpers ------------------ */
async function startWebcam() {
  if (stream) return; // déjà actif

  try {
    stream = await navigator.mediaDevices.getUserMedia({ video: true });
    video.srcObject = stream;
    await video.play();

    // Démarrer les captures régulières
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

async function captureFrameAndPredict() {
  if (!video.videoWidth || !video.videoHeight) return; // webcam pas encore prête

  const canvas = document.createElement('canvas');
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  const ctx = canvas.getContext('2d');
  ctx.drawImage(video, 0, 0);
  const dataURL = canvas.toDataURL('image/png');

  // Vérification basique du contenu
  if (!dataURL.startsWith('data:image/png;base64,')) return;

  // Optionnel : éviter d'envoyer des images trop petites
  const base64Data = dataURL.split(',')[1];
  if (base64Data.length < MIN_IMAGE_SIZE) return;

  try {
    const res  = await fetch('/predict_webcam_frame', {
      method : 'POST',
      headers: { 'Content-Type': 'application/json' },
      body   : JSON.stringify({ image: dataURL })
    });

    const data = await res.json();

    if (data.prediction) {
      predictionText.textContent = data.prediction;
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
  if (radioWebcam.checked) startWebcam();
  else                     stopWebcam();   // upload sélectionné
}

radioUpload.addEventListener('change', handleSourceChange);
radioWebcam.addEventListener('change', handleSourceChange);
window.addEventListener('beforeunload', stopWebcam); // nettoyage

// Si la page se recharge avec webcam déjà cochée
if (radioWebcam.checked) startWebcam();
