#!/usr/bin/env perl

use strict;
use HTML::Strip;
use URI::Encode;
use String::Util qw(trim collapse);

my $html = HTML::Strip->new;
my $uri = URI::Encode->new({encode_reserved => 1});
my $file;

foreach $file (<"Pandoc.docset/Contents/Resources/Documents/pandoc.org/*.html">) {
	local $/;

	open PAGE, "<$file" or die "$file: $!";
	$_ = <PAGE>;
	close PAGE or warn "$file: " . ($! || "Exit status $?");
	open PAGE, ">$file" or die "$file: $!";

	s{<li>\s*<a href="MANUAL\.pdf">User's Guide \(PDF\)</a>\s*(</li>)?\s*}{}ig;
	s{try/index\.html}{http://try.pandoc.org/}ig;
	s{index-2\.html}{index.html}ig;
	s{<script[^>]*>.*?</script>\s*}{}igs;
	s{<div[^>]* id="(flattr|toc)"[^>]*>.*?</div>\s*}{}igs;
	s{<h[2-6][^>]* id="[\w-]+"[^>]*>(.*?)</h[2-6]>}{
		'<a name="//apple_ref/cpp/'
		. make_path($1)
		. "\" class=\"dashAnchor\"></a>\n$&"
	}eigs;

	$html->eof;
	print PAGE;
	close PAGE or warn "$file: " . ($! || "Exit status $?");
}

sub make_path {
	my $text = shift;
	my $type = 'Section';

	if ($text =~ /Extension: ?/i) {
		$text =~ s///;
		$type = 'Extension';
	}
	return "$type/" . $uri->encode(collapse(trim($html->parse($text))));
}
