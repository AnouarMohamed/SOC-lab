<?php
/**
 * Atlas Distribution - Logistics & Orders REST API
 * Endpoint: /api/orders.php
 */

header('Content-Type: application/json');
require_once __DIR__ . '/../db.php';

if (!$pdo) {
    http_response_code(503);
    echo json_encode(["status" => "error", "message" => "Database backend unavailable"]);
    exit;
}

$limit = isset($_GET['limit']) ? min((int)$_GET['limit'], 100) : 25;
$offset = isset($_GET['offset']) ? (int)$_GET['offset'] : 0;

try {
    $stmt = $pdo->prepare("
        SELECT 
            o.order_number,
            o.total_amount_eur,
            o.order_status,
            o.shipping_tracking_number,
            o.order_timestamp,
            w.location_name as warehouse,
            c.billing_city as destination_city
        FROM logistics.orders o
        JOIN logistics.warehouses w ON o.warehouse_id = w.warehouse_id
        JOIN crm.customers c ON o.customer_id = c.customer_id
        ORDER BY o.order_id DESC
        LIMIT :limit OFFSET :offset
    ");
    $stmt->bindValue(':limit', $limit, PDO::PARAM_INT);
    $stmt->bindValue(':offset', $offset, PDO::PARAM_INT);
    $stmt->execute();

    $orders = $stmt->fetchAll();
    echo json_encode([
        "status" => "success",
        "returned_records" => count($orders),
        "limit" => $limit,
        "offset" => $offset,
        "data" => $orders
    ], JSON_PRETTY_PRINT);
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(["status" => "error", "message" => $e->getMessage()]);
}
