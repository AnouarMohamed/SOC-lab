<?php
require_once __DIR__ . '/db.php';

$customer_count = 0;
$order_count = 0;
$warehouse_count = 0;
$db_status = "DISCONNECTED";

if ($pdo) {
    try {
        $stmt = $pdo->query("SELECT COUNT(*) AS total FROM crm.customers");
        $customer_count = $stmt->fetch()['total'];

        $stmt = $pdo->query("SELECT COUNT(*) AS total FROM logistics.orders");
        $order_count = $stmt->fetch()['total'];

        $stmt = $pdo->query("SELECT COUNT(*) AS total FROM logistics.warehouses");
        $warehouse_count = $stmt->fetch()['total'];

        $db_status = "ONLINE (SRV-DB-01)";
    } catch (Exception $e) {
        $db_status = "ERROR: " . $e->getMessage();
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Atlas Distribution S.A. - Enterprise Operations Gateway</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #0f172a; color: #f1f5f9; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        .navbar-brand { font-size: 1.15rem; font-weight: 700; letter-spacing: 0.05em; }
        .hero { background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%); border-bottom: 1px solid #334155; }
        .card { background-color: #1e293b; border: 1px solid #334155; border-radius: 6px; }
        .badge-live { background-color: #059669; }
        .metric-label { font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; color: #94a3b8; }
        .metric-value { font-size: 2.2rem; font-weight: 700; color: #38bdf8; }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark bg-dark px-4 border-bottom border-secondary">
        <span class="navbar-brand text-light">ATLAS DISTRIBUTION S.A. | SUPPLY CHAIN PLATFORM</span>
        <div class="d-flex align-items-center gap-2">
            <span class="badge bg-secondary">TIER: SRV-WEB-01</span>
            <span class="badge <?= $pdo ? 'badge-live' : 'bg-danger' ?>">DB: <?= htmlspecialchars($db_status) ?></span>
        </div>
    </nav>

    <div class="hero py-5 text-center">
        <div class="container">
            <h1 class="h2 fw-bold mb-2">Central Supply Chain & Enterprise Directory</h1>
            <p class="text-secondary mx-auto mb-4" style="max-width: 650px;">
                Critical retail infrastructure managing European vendor logistics, high-volume order dispatching, and enterprise customer account databases.
            </p>
            <div class="d-flex justify-content-center gap-3">
                <a href="upload.php" class="btn btn-outline-info px-4 py-2 font-monospace">B2B Document Ingestion Gateway</a>
                <a href="api/orders.php" class="btn btn-secondary px-4 py-2 font-monospace">Orders REST API</a>
                <a href="metrics.php" class="btn btn-dark px-4 py-2 font-monospace border-secondary">Prometheus Telemetry</a>
            </div>
        </div>
    </div>

    <div class="container py-5">
        <div class="row g-4">
            <div class="col-md-4">
                <div class="card p-4">
                    <span class="metric-label">Managed Customer Directory (PII)</span>
                    <div class="metric-value"><?= number_format($customer_count) ?></div>
                    <small class="text-secondary">GDPR Scope: Article 33/34 Regulated Records</small>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card p-4">
                    <span class="metric-label">Active Warehouse Orders</span>
                    <div class="metric-value"><?= number_format($order_count) ?></div>
                    <small class="text-secondary">Logistics Schema: Roissy, Saint-Quentin, Fos-sur-Mer</small>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card p-4">
                    <span class="metric-label">Operational Hubs</span>
                    <div class="metric-value"><?= number_format($warehouse_count) ?></div>
                    <small class="text-secondary">Backup Daemon: svc-backup (Scheduled 02:00 UTC)</small>
                </div>
            </div>
        </div>
    </div>

    <footer class="footer mt-auto py-3 bg-dark text-center text-secondary border-top border-secondary">
        <div class="container font-monospace" style="font-size: 0.8rem;">
            [CONFIDENTIAL] Atlas Distribution S.A. | Detection & Incident Response Range INC-ATLAS-001
        </div>
    </footer>
</body>
</html>
