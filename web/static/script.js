function updateData() {
  fetch("/data")
    .then((response) => response.json())
    .then((data) => {
      document.getElementById("cloud-cover").textContent =
        data.cloud_cover || "-";
      document.getElementById("sky-condition").textContent =
        data.sky_condition || "-";
      document.getElementById("confidence").textContent =
        data.confidence_score + "%" || "-";
      document.getElementById(
        "metadata"
      ).textContent = `1080x1080, 1.1mm, f/2.2, ${data.shutter_speed}, ISO ${data.iso}`;
      document.getElementById(
        "last-captured"
      ).textContent = `Last Captured : ${data.timestamp}`;

      const img = document.getElementById("latest-image");
      img.src = "static/img/latest_capture.jpg?rand=" + new Date().getTime(); // cache-bypass
    });
}

setInterval(updateData, 5000); // update tiap 5 detik
updateData(); // initial load
