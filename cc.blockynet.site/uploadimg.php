<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);
header("Content-Type: application/json");

// Base folder
$base_dir = __DIR__ . "/images/";

// Ambil parameter (POST form-data)
$type = isset($_POST['type']) ? preg_replace('/[^a-z]/', '', $_POST['type']) : '';
$date = isset($_POST['date']) ? preg_replace('/[^0-9]/', '', $_POST['date']) : '';
$file = $_FILES['image'] ?? null;

// Validasi minimal
if (!$type || !$date || !$file) {
    http_response_code(400);
    echo json_encode(["error" => "Param type/date/image wajib"]);
    exit;
}

// Hanya izinkan tipe 'raw' atau 'segmented'
if (!in_array($type, ['raw', 'segmented'])) {
    http_response_code(400);
    echo json_encode(["error" => "Tipe hanya boleh raw/segmented"]);
    exit;
}

// Pastikan folder tujuan ada, jika tidak buat
$target_dir = $base_dir . "$type/$date/";
if (!file_exists($target_dir)) {
    if (!mkdir($target_dir, 0777, true)) {
        http_response_code(500);
        echo json_encode(["error" => "Gagal membuat folder $target_dir"]);
        exit;
    }
}

// Simpan file ke folder sesuai tipe dan tanggal
$target_file = $target_dir . basename($file['name']);

if (!move_uploaded_file($file['tmp_name'], $target_file)) {
    http_response_code(500);
    echo json_encode(["error" => "Gagal upload file: $target_file"]);
    exit;
}

// Path web (untuk disimpan di DB jika mau)
$web_path = "images/$type/$date/" . basename($file['name']);

echo json_encode([
    "success" => true,
    "message" => "Upload sukses ke $web_path",
    "file_path" => $web_path
]);
?>