<?php

putenv('LANG=en_US.UTF-8');

$output = "";

if (!isset($_GET['p'])) die;

$bar = $_GET['p'];

switch ($bar) {
	case 'mw':
	case 'op':
	case 'craft':
		$parser = "./parsers/".$bar."parser.py";
		$file = "cache/".$bar.".json";
		break;
	default:
		die("'mw', 'op' or 'craft'\n");
}

// Handle caching
$modtime = filemtime($file);
$curtime = time();

if ($curtime > $modtime + 300) {
	shell_exec($parser." json > ".$file);
}

// Read cached file
$output = shell_exec("(cat ".$file." | ./tools/json2table.py)");
$titles = shell_exec("(cat ".$file." | ./tools/json2titles.py)");

// For browsers
if (stripos($_SERVER['HTTP_USER_AGENT'], "Mozilla") !== false) {
	print "<head><title>".$titles."</title></head>\n";
	$output = "<pre>".$output."</pre>";
}

// Short version for IRC
if (isset($_GET['t']) && $_GET['t'] == "irc") {
	print($titles);
} else {
	print($output);
}
?>
