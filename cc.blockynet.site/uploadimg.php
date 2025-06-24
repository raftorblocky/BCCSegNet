<?php
$target_dir = __DIR__ . "/static/img/";
$target_url_path = "static/img/";

if (!isset($_FILES['image'])) {
    die("Tidak ada file dikirim.");
}

$file = $_FILES["image"];
$target_file = $target_dir . basename($file["name"]);

if (!file_exists($target_dir)) {
    die("Folder tujuan tidak ditemukan: $target_dir");
}

if (!is_writable($target_dir)) {
    die("Folder tidak bisa ditulis: $target_dir");
}

if (move_uploaded_file($file["tmp_name"], $target_file)) {
    echo "Upload berhasil ke: " . $target_url_path . basename($file["name"]);
} else {
    echo "Gagal memindahkan file dari tmp.";
}
?>
