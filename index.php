<?php

putenv('LANG=en_US.UTF-8');

$output = "";

if (!isset($_GET['p'])){
	$bar = 'all';
} else {
	$bar = $_GET['p'];
}

switch ($bar) {
	case 'mw':
	case 'op':
	case 'craft':
	case 'fa':
	case 'pa':
	case 'bg':
	case 'dno':
        //case 'u2pb':
        //case 'u2pt':
		$update = "./tools/update_cache.sh ".$bar;
		$file = "cache/".$bar.".json";
		break;
	case 'all':
		$update = "";
		$file = 'cache/op.json cache/mw.json cache/craft.json cache/jbm.json cache/fa.json cache/bg.json cache/dno.json cache/u2pb.json cache/u2pt.json';
		break;
	case 'history':
		die("<pre>".shell_exec("(cat ./log/beerlog.json | tail -n 50 | ./tools/log2table.py)")."</pre>");
		break;
	default:
		die("'mw', 'op', 'craft', 'all' or 'history'\n");
}

// Handle caching
if (!empty($update)) {
	$modtime = filemtime($file);
	$curtime = time();

	if ($curtime > $modtime + 300) {
		shell_exec($update);
	}
}

// Read cached file(s)
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
