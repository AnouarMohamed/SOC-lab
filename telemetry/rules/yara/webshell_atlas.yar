/*
    Atlas Distribution - Incident Response Artifact Scanner
    Rule: Atlas_PHP_Webshell_Detection
    Scenario: INC-ATLAS-001 (Server Compromise via File Upload)
*/

rule Atlas_PHP_Webshell_Generic {
    meta:
        description = "Identifies PHP webshells exploiting file upload directories via execution wrappers"
        author = "Atlas DFIR Team"
        date = "2026-10-01"
        incident = "INC-ATLAS-001"
        mitre_technique = "T1505.003"
        severity = "High"

    strings:
        // Dangerous execution functions
        $f_exec = "exec(" ascii nocase
        $f_sys = "system(" ascii nocase
        $f_pass = "passthru(" ascii nocase
        $f_shell = "shell_exec(" ascii nocase
        $f_popen = "popen(" ascii nocase
        $f_proc = "proc_open(" ascii nocase

        // Input vectors
        $inp_req = "$_REQUEST[" ascii
        $inp_post = "$_POST[" ascii
        $inp_get = "$_GET[" ascii
        $inp_cookie = "$_COOKIE[" ascii

        // Obfuscation / decoding techniques
        $o_b64 = "base64_decode" ascii nocase
        $o_gz = "gzinflate" ascii nocase
        $o_eval = "eval(" ascii nocase
        $o_assert = "assert(" ascii nocase

        // Lab specific markers
        $tag_atlas = "atlas_pwn" ascii
        $tag_redteam = "atlas_redteam" ascii

    condition:
        (
            // Direct execution paired with user input
            (any of ($f_*) and any of ($inp_*)) or
            // Obfuscation combination
            (any of ($o_eval, $o_assert) and any of ($o_b64, $o_gz)) or
            // Specific incident artifact signatures
            any of ($tag_atlas, $tag_redteam)
        ) and filesize < 500KB
}
