function updateData() {
  fetch("data.php")
    .then((res) => res.json())
    .then((data) => {
      if (data.error) {
        console.warn(data.error);
        return;
      }

      document.getElementById("cloud-cover").textContent =
        data.cloud_cover + "%";
      document.getElementById("cloud-okta").textContent =
        data.cloud_okta + " Okta";
      document.getElementById("sky-condition").textContent = data.sky_condition;
      document.getElementById("last-captured").textContent =
        "Last Captured : " + data.timestamp;
      document.getElementById("metadata").textContent = data.metadata;

      // Refresh gambar juga
      const img = document.getElementById("latest-image");
      img.src = "static/img/latest_capture.jpg?_=" + new Date().getTime();
    })
    .catch((err) => console.error("Gagal ambil data:", err));
}

updateData();

// Update otomatis setiap 5 detik
setInterval(updateData, 5000);
