let lastTimestamp = "";

function updateData() {
  fetch("data.php")
    .then((res) => res.json())
    .then((data) => {
      if (data.error) return;

      if (data.timestamp !== lastTimestamp) {
        lastTimestamp = data.timestamp;

        document.getElementById("cloud-cover").textContent =
          data.cloud_cover + "%";
        document.getElementById("cloud-okta").textContent =
          data.cloud_okta + " Okta";
        document.getElementById("sky-condition").textContent =
          data.sky_condition;
        document.getElementById("last-captured").textContent =
          "Last Captured : " + data.timestamp;
        document.getElementById("metadata").textContent = data.metadata;

        // Pakai file_path dari backend, preload untuk mencegah flicker
        const newImg = new Image();
        newImg.onload = () => {
          document.getElementById("latest-image").src = newImg.src;
        };
        newImg.src = data.file_path;
      }
    })
    .catch((err) => console.error("Gagal ambil data:", err));
}

updateData();
setInterval(updateData, 5000);
