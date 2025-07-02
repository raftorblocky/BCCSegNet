<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);
header("Content-Type: application/json");

// DB Config
$host = "localhost";
$user = "blockyne_admin";
$password = "!Blocky1js";
$database = "blockyne_cloud";

$conn = new mysqli($host, $user, $password, $database);
if ($conn->connect_error) {
    http_response_code(500);
    echo json_encode(["error" => "DB connection failed"]);
    exit;
}

// Ambil data klasifikasi terbaru, SEKALIAN file_path-nya
$sql = "SELECT 
            c.cloud_cover, c.sky_status, c.cloud_okta,
            i.capture_time, i.resolution, i.focal_length, i.aperture, i.shutter_speed, i.iso,
            i.file_path
        FROM Classifications c
        JOIN Images i ON i.image_id = c.image_id
        ORDER BY i.capture_time DESC LIMIT 1";

$result = $conn->query($sql);
if ($row = $result->fetch_assoc()) {
    echo json_encode([
        "cloud_cover" => $row["cloud_cover"],
        "cloud_okta" => $row["cloud_okta"],
        "sky_condition" => $row["sky_status"],
        "timestamp" => $row["capture_time"],
        "metadata" => "{$row['resolution']}, {$row['focal_length']}mm, {$row['aperture']}, {$row['shutter_speed']}, ISO {$row['iso']}",
        "file_path" => $row["file_path"]   
    ]);
} else {
    echo json_encode(["error" => "No data found"]);
}

$conn->close();
?>