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

# Skywalker setup

if ($ENV{HTTP_HOST} =~/skywalker.lansce.lanl.gov/) {
  $outdir  = "/var/www/html/nano/Output";
}
# Local MAC setup

elsif ($ENV{HTTP_HOST} =~/localhost/) {
  $outdir  = "/Library/WebServer/Documents/nano/Output";
}

# LANL server setup (development)

elsif ($ENV{HTTP_HOST} =~/totalscattering.ds.lanl.gov/) {
  $outdir  = "/var/www/html/yellow/development/dev-green/docs/wrtout/projects/tscattering/nano/Output";
}

elsif ($ENV{HTTP_HOST} =~/totalscattering.lanl.gov/) {
  $outdir  = "/var/www/html/green/docs/wrtout/projects/tscattering/nano/Output";
}

#----------------------------------------------------------------------------

if (-r "$outdir/$file.$type") {
  print $cgi->header(-type=>"application/$type",-attachment=>"nano.$type");
  open (OUT,"$outdir/$file.$type"); while (<OUT>) {print $_;} close OUT;
}

