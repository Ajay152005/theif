document.addEventListener('DOMContentLoaded', function() {
  const videoContainer = document.getElementById('videoContainer');
  const webcamBtn = document.getElementById('webcamBtn');
  const stopBtn = document.getElementById('stopBtn');
  let streaming = false;
  let video = document.createElement('video');

  // Function to start webcam feed
  function startWebcam() {
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      navigator.mediaDevices.getUserMedia({ video: true })
        .then(function(stream) {
          video.srcObject = stream;
          video.play();
          videoContainer.appendChild(video);
          video.style.width = '100%';
          video.style.height = '100%';

          const aspectRatio = video.videoWidth / video.videoHeight;
          const containerWidth = videoContainer.offsetWidth;
          const containerHeight = containerWidth / aspectRatio;

          if (containerHeight > videoContainer.offsetHeight) {
            const newWidth = video.videoWidth / (video.videoHeight / videoContainer.offsetHeight);
            video.style.width = `${newWidth}px`;
            video.style.height = `${videoContainer.offsetHeight}px`;
          } else {
            video.style.width = `${containerWidth}px`;
            video.style.height = `${containerHeight}px`;
          }

          streaming = true;
          console.log('Webcam started. Streaming:', streaming);
        })
        .catch(function(error) {
          console.error('Error accessing webcam:', error);
        });
    } else {
      console.error('getUserMedia not supported');
    }
  }

  // Function to stop capturing
  function stopCapturing() {
    if (video.srcObject) {
      video.srcObject.getTracks().forEach(track => track.stop());
      video.removeAttribute('src');
      video.load();
      videoContainer.removeChild(video);
      streaming = false;
      console.log('Streaming:', streaming);
    }
  }

  // Event listeners for buttons
  webcamBtn.addEventListener('click', function() {
    if (!streaming) {
      startWebcam();
    }
  });

  stopBtn.addEventListener('click', function() {
    if (streaming) {
      stopCapturing();
    }
  });
});