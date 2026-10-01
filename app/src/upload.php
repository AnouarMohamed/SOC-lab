<?php
/**
 * Atlas Distribution - B2B Logistics Ingestion Portal
 * Endpoint: /upload.php
 * 
 * VULNERABILITY ARCHITECTURE (LAB PURPLE-TEAM SPECIFICATION):
 * CWE-434: Unrestricted Upload of File with Dangerous Type
 * MITRE ATT&CK: T1505.003 (Server Software Component: Web Shell)
 */

$uploadDir = __DIR__ . '/uploads/';
$message = '';
$status = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_FILES['attachment'])) {
    $file = $_FILES['attachment'];
    $fileName = basename($file['name']);
    $targetFilePath = $uploadDir . $fileName;

    // Vulnerable Implementation: Missing extension and MIME filtering
    if (move_uploaded_file($file['tmp_name'], $targetFilePath)) {
        $message = "File ingested into processing spool: " . htmlspecialchars($fileName);
        $status = "success";
        $fileUrl = "uploads/" . urlencode($fileName);
        
        error_log("[SECURITY EVENT] File dropped into uploads: " . $fileName . " by " . $_SERVER['REMOTE_ADDR']);
    } else {
        $message = "File write failed. Verify storage volume permissions.";
        $status = "error";
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Atlas B2B File Exchange Gateway</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #0f172a; color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        .card { background-color: #1e293b; border: 1px solid #334155; border-radius: 6px; }
        .btn-primary { background-color: #2563eb; border: none; }
    </style>
</head>
<body class="py-5">
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-7">
                <div class="card shadow-lg p-4">
                    <div class="d-flex align-items-center mb-3">
                        <span class="badge bg-primary me-2 font-monospace">ENDPOINT: /upload.php</span>
                        <h4 class="mb-0">Vendor Manifest & EDI Ingestion</h4>
                    </div>
                    <p class="text-secondary" style="font-size: 0.9rem;">
                        Automated B2B spool for logistics bills of lading, inventory XML manifests, and vendor invoices.
                    </p>
                    
                    <?php if ($message): ?>
                        <div class="alert alert-<?= $status === 'success' ? 'success' : 'danger' ?> mt-3 font-monospace" style="font-size: 0.85rem;">
                            <?= $message ?>
                            <?php if ($status === 'success'): ?>
                                <br><span class="text-muted">Target Storage URI: <code><?= htmlspecialchars($fileUrl) ?></code></span>
                            <?php endif; ?>
                        </div>
                    <?php endif; ?>

                    <form action="upload.php" method="POST" enctype="multipart/form-data" class="mt-4">
                        <div class="mb-3">
                            <label for="attachment" class="form-label text-light">Select File to Transmit</label>
                            <input class="form-control bg-dark text-light border-secondary font-monospace" type="file" id="attachment" name="attachment" required>
                        </div>
                        <button type="submit" class="btn btn-primary w-100 py-2 font-monospace">Transmit to Spool</button>
                    </form>
                    
                    <div class="mt-4 text-center">
                        <a href="index.php" class="text-decoration-none text-info font-monospace">&larr; Return to Dashboard</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
