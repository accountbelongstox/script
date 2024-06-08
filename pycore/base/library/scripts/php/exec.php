<?php
if ($argc < 2) {
    echo "Usage: php run_bat.php <path_to_bat_file>\n";
    exit(1);
}

$bat_file = $argv[1];

if (!file_exists($bat_file)) {
    echo "Error: File not found - " . $bat_file . "\n";
    exit(1);
}

$output = [];
$return_var = 0;
exec($bat_file, $output, $return_var);

print_r($output);
echo "Return value: " . $return_var . "\n";
?>
