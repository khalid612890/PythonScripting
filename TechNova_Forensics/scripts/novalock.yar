rule NovaLock_Ransomware_Indicators
{
  meta: author = "TechNova IR (coursework)" description = "Strings observed in NovaLock samples (lab)"
  strings:
    $note   = "=== NOVALOCK ===" ascii
    $ext    = ".novalock" ascii
    $c2     = "cdn-update-sync.net" ascii
    $btc    = "bc1qnv7l0ck9x2t4h5m8r3e6w0q1z7y4u2p9s5d3f" ascii
    $ua     = "NovaLock/2.1" ascii
    $vss    = "vssadmin delete shadows" ascii nocase
    $gate   = "/gate.php" ascii
  condition: 3 of them
}
rule Office_Macro_Downloader
{
  strings: $a = "AutoOpen" ascii  $b = "powershell" ascii nocase  $c = "DownloadString" ascii  $d = "WScript.Shell" ascii
  condition: 3 of them
}
