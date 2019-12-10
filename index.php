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
		$file = "tmp/".$bar.".txt";
break;
	default:
		die("'mw', 'op' or 'craft'\n");
}

// Handle caching
$modtime = filemtime($file);
$curtime = time();

if ($curtime > $modtime + 300) {
	shell_exec($parser." > ".$file);
}

// Read cached file
$output = file_get_contents($file);

function get_beer_names($string)
{
	$lines = explode("\n", $string);
	$delimiters = explode("  ", $lines[1]);
	$beer_len = strlen($delimiters[0]);

	for  ($i = 2; $i < count($lines) -1; $i++) {
		$beer_names[] = rtrim(mb_substr($lines[$i], 0, $beer_len));
	}

	return implode(" | ", $beer_names);
}

// For browsers
if (stripos($_SERVER['HTTP_USER_AGENT'], "Mozilla") !== false) {
	print "<head><title>".get_beer_names($output)."</title></head>\n";
	$output = "<pre>".$output."</pre>";
}

// Short version for IRC
if (isset($_GET['t']) && $_GET['t'] == "irc") {
	print get_beer_names($output);
} else {
	print($output);
}
?>
