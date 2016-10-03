#!/usr/bin/perl
#----------------------------------------------------------------------------

use CGI;
use FindBin qw($RealBin);

#----------------------------------------------------------------------------

$cgi=CGI::new();

$file   = $cgi->param('FILE');

# Skywalker setup

if ($ENV{HTTP_HOST} =~/skywalker.lansce.lanl.gov/) {
  $outdir  = "/var/www/html/nano/Output";
  $wwwout  = "/nano/Output/";
}
# Local MAC setup

elsif ($ENV{HTTP_HOST} =~/localhost/) {
  $outdir  = "/Library/WebServer/Documents/nano/Output";
  $wwwout  = "/nano/Output/";
}

# LANL server setup (development)

elsif ($ENV{HTTP_HOST} =~/totalscattering.ds.lanl.gov/) {
  $outdir  = "/var/www/html/yellow/development/dev-green/docs/wrtout/projects/tscattering/nano/Output";
  $wwwout  = "http://dev-g.lanl.gov/wrtout/projects/tscattering/nano/Output/";
}

# LANL server setup

elsif ($ENV{HTTP_HOST} =~/totalscattering.lanl.gov/) {
  $outdir  = "/var/www/html/green/docs/wrtout/projects/tscattering/nano/Output";
  $wwwout  = "http://www.lanl.gov/wrtout/projects/tscattering/nano/Output/";
}

#----------------------------------------------------------------------------

print $cgi->header()."\n";
print "<html>\n";
&print_plot();
print "</html>\n";

#----------------------------------------------------------------------------

sub print_plot {
  $m='Start ';
  if (-r "$outdir/$file") {
    unless (-r "$outdir/$file.xml") {
      if ($file=~/.pow/) {$xl="Q (A^-1)"; $yl="Intensity"; $n="Powder";}
      if ($file=~/.gr/)  {$xl="r (A)"; $yl="G(r)"; $n="PDF";}

      open (XML, ">$outdir/$file.xml");
      print XML "<?xml version=\"1.0\" standalone=\"no\"?>\n";
      print XML "<!DOCTYPE plot SYSTEM \"/ptplot/PlotML_1.dtd\">\n";
      print XML "<!-- Ptolemy plot, version 3.1, PlotML format. -->\n";
      print XML "<plot>\n";
      print XML "<title></title>\n";
      print XML "<xLabel>$xl</xLabel>\n";
      print XML "<yLabel>$yl</yLabel>\n";
      print XML "<default connected=\"yes\" marks=\"none\"/>\n";
      print XML "<dataset name=\"$n\" connected=\"yes\" >\n";
      open (I, "$outdir/$file");
      while ($line=<I>) {
        $line=~s/^\s*//; my ($x,$y)=split(/\s+/,$line);
        if (($x=~/[0-9]/) && ($y=~/[0-9]/)) {
          print XML "<p x=\"$x\" y=\"$y\"/>\n";
        }
      }
      close I;
      print XML "</dataset>\n";
      print XML "</plot>\n";
      close XML;
    }
    print "<h3>Plot of $file - $m..</h3>\n";
    print "<p><applet\n";
    print " code=\"ptolemy.plot.plotml.PlotMLApplet\"\n";
    print " codebase=\"/ptplot\"\n";
    print " archive=\"plotmlapplet.jar\"\n";
    print " width=\"650\"\n";
    print " height=\"450\"\n";
    print ">\n";
    print "<param name=\"background\" value=\"#FFFFFF\" >\n";
    print "<param name=\"dataurl\" value=\"$wwwout/$file.xml\" >\n";
    print " No Java Plug-in support for applet, see\n";
    print "<a href=\"http://java.sun.com/products/plugin/\">\n";
    print "<code>http://java.sun.com/products/plugin/</code></a>\n";
    print "</applet></p>\n";
  } else {
    print "<h3>File $file not found ..</h3>\n";
  }
}

