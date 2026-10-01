<?php
/**
 * Prometheus Telemetry Exporter Endpoint
 * URI: /metrics.php
 */

header('Content-Type: text/plain; version=0.0.4');

require_once __DIR__ . '/db.php';

$customer_count = 0;
$order_count = 0;
$db_up = 0;

if ($pdo) {
    try {
        $stmt = $pdo->query("SELECT COUNT(*) AS total FROM crm.customers");
        $customer_count = (int)$stmt->fetch()['total'];
        $stmt = $pdo->query("SELECT COUNT(*) AS total FROM logistics.orders");
        $order_count = (int)$stmt->fetch()['total'];
        $db_up = 1;
    } catch (Exception $e) {
        $db_up = 0;
    }
}

$upload_files = 0;
$upload_dir = __DIR__ . '/uploads/';
if (is_dir($upload_dir)) {
    $files = scandir($upload_dir);
    $upload_files = count($files) - 2; // exclude . and ..
}

echo "# HELP atlas_http_database_up Database connection health\n";
echo "# TYPE atlas_http_database_up gauge\n";
echo "atlas_http_database_up $db_up\n\n";

echo "# HELP atlas_crm_customer_records_total Total customer records under management\n";
echo "# TYPE atlas_crm_customer_records_total gauge\n";
echo "atlas_crm_customer_records_total $customer_count\n\n";

echo "# HELP atlas_logistics_orders_total Total processed supply chain orders\n";
echo "# TYPE atlas_logistics_orders_total counter\n";
echo "atlas_logistics_orders_total $order_count\n\n";

echo "# HELP atlas_upload_directory_files_count Current files located in upload landing zone\n";
echo "# TYPE atlas_upload_directory_files_count gauge\n";
echo "atlas_upload_directory_files_count $upload_files\n";
