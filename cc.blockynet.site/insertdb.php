<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);
header("Content-Type: application/json");

// Konfigurasi DB
$host = "localhost";
$user = "blockyne_admin";
$password = "!Blocky1js";
$database = "blockyne_cloud";

// Ambil data dari request POST
$data = json_decode(file_get_contents("php://input"), true);

// Validasi field yang wajib ada
$required_fields = ['file_path', 'capture_time', 'latitude', 'longitude',
    'camera_model', 'resolution', 'aperture', 'focal_length',
    'shutter_speed', 'iso',
    'cloud_cover', 'cloud_okta', 'sky_status'];

foreach ($required_fields as $field) {
    if (!isset($data[$field])) {
        http_response_code(400);
        echo json_encode(["error" => "Field '$field' is missing."]);
        exit;
    }
}

// Koneksi DB
$conn = new mysqli($host, $user, $password, $database);
if ($conn->connect_error) {
    http_response_code(500);
    echo json_encode(["error" => "Koneksi gagal: " . $conn->connect_error]);
    exit;
}

// Insert ke tabel Images
$stmt1 = $conn->prepare("INSERT INTO Images (
    file_path, capture_time, latitude, longitude,
    camera_model, resolution, aperture, focal_length,
    shutter_speed, iso
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)");

$stmt1->bind_param("sssissssss",
    $data['file_path'],
    $data['capture_time'],
    $data['latitude'],
    $data['longitude'],
    $data['camera_model'],
    $data['resolution'],
    $data['aperture'],
    $data['focal_length'],
    $data['shutter_speed'],
    $data['iso']
);

if (!$stmt1->execute()) {
    http_response_code(500);
    echo json_encode(["error" => "Insert ke Images gagal: " . $stmt1->error]);
    exit;
}

$image_id = $stmt1->insert_id;

// Insert ke tabel Classifications
$stmt2 = $conn->prepare("INSERT INTO Classifications (
    image_id, cloud_cover, cloud_okta, sky_status
) VALUES (?, ?, ?, ?)");

$stmt2->bind_param("idis",
    $image_id,
    $data['cloud_cover'],
    $data['cloud_okta'],
    $data['sky_status']
);

if (!$stmt2->execute()) {
    http_response_code(500);
    echo json_encode(["error" => "Insert ke Classifications gagal: " . $stmt2->error]);
    exit;
}

// Sukses
$conn->close();
echo json_encode(["success" => true, "message" => "Data berhasil dimasukkan."]);
?>
