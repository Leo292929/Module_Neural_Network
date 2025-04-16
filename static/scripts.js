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

/* ----------- Webcam helpers ------------------ */
async function startWebcam() {
  if (stream) return;                  // déjà actif
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

async function captureFrameAndPredict() {
  if (!video.videoWidth) return;       // vidéo pas encore prête
  const canvas = document.createElement('canvas');
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  canvas.getContext('2d').drawImage(video, 0, 0);
  const dataURL = canvas.toDataURL('image/png');

  try {
    const res  = await fetch('/predict_webcam_frame', {
      method : 'POST',
      headers: { 'Content-Type': 'application/json' },
      body   : JSON.stringify({ image: dataURL })
    });
    const data = await res.json();
    if (data.prediction) predictionText.textContent = data.prediction;
  } catch (err) {
    console.error('Prediction error:', err);
    stopWebcam();
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
