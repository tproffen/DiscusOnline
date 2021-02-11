#!/usr/bin/perl
#----------------------------------------------------------------------------
# File access to GSA, PDF and other files.
# (c) Thomas Proffen, 2008
#----------------------------------------------------------------------------

use CGI;

#----------------------------------------------------------------------------

$cgi=CGI::new();

$file   = $cgi->param('file');
$type   = $cgi->param('type');

$outdir  = "/var/www/html/DiscusOnline/nano/Output";

#----------------------------------------------------------------------------

if (-r "$outdir/$file.$type") {
  print $cgi->header(-type=>"application/$type",-attachment=>"nano.$type");
  open (OUT,"$outdir/$file.$type"); while (<OUT>) {print $_;} close OUT;
}

