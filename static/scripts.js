const video = document.getElementById('video');
const captureBtn = document.getElementById('captureBtn');
const webcamImageInput = document.getElementById('webcam_image');

// Demander l'accès à la webcam
navigator.mediaDevices.getUserMedia({ video: true })
  .then(stream => {
    video.srcObject = stream;
  })
  .catch(err => {
    console.error("Erreur d'accès à la webcam:", err);
  });

// Quand on clique sur "Capturer"
captureBtn.addEventListener('click', () => {
  const canvas = document.createElement('canvas');
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  canvas.getContext('2d').drawImage(video, 0, 0);

  const dataUrl = canvas.toDataURL('image/png');
  // dataUrl = "data:image/png;base64,iVBORw0K..."
  webcamImageInput.value = dataUrl;
});
