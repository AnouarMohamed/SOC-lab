<?php
/**
 * Atlas Distribution - Database Connection Configuration
 * Target: SRV-DB-01 (Internal Postgres Cluster)
 * 
 * SECURITY NOTICE: Sensitive configuration file.
 * In the unhardened baseline, this configuration contains plaintext credentials
 * stored inside the web root, exposing it to read access upon LFI or webshell compromise.
 */

$db_host = getenv('DB_HOST') ?: 'srv-db-01';
$db_port = getenv('DB_PORT') ?: '5432';
$db_name = getenv('DB_NAME') ?: 'atlas_db';
$db_user = getenv('DB_USER') ?: 'atlas_admin';
$db_pass = getenv('DB_PASS') ?: 'AtlasSecPass2026!';

try {
    $dsn = "pgsql:host={$db_host};port={$db_port};dbname={$db_name};";
    $pdo = new PDO($dsn, $db_user, $db_pass, [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        PDO::ATTR_TIMEOUT => 5
    ]);
} catch (PDOException $e) {
    // In production we avoid leaking detailed connection errors to client
    $pdo = null;
    error_log("DB Connection Failure: " . $e->getMessage());
}
