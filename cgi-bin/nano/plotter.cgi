#!/usr/bin/perl
#----------------------------------------------------------------------------

use CGI;
use FindBin qw($RealBin);

#----------------------------------------------------------------------------

$cgi=CGI::new();

$file   = $cgi->param('FILE');
$title   = $cgi->param('TITLE');

$wwwroot = "/discus";
$outdir  = "/var/www/html/DiscusOnline/nano/Output";
$wwwout  = "/discus/nano/Output/";

#----------------------------------------------------------------------------

print $cgi->header()."\n";
print "<html>\n";
print "<body>\n";
print "<head>\n";
print "<link href=\"$wwwroot/styles/discus.css\" ";
print "      rel=\"stylesheet\"  type=\"text/css\">\n";
print "  <script src=\"$wwwroot/scripts/plotly-latest.min.js\"></script>\n";
print "</head>\n";
print "<body>\n";

&print_plot();

print "</body>\n";
print "</html>\n";

#----------------------------------------------------------------------------

sub print_plot {
  if (-r "$outdir/$file") {
    if ($file=~/.pow/) {$xl="Q (A^-1)"; $yl="Intensity"; $n="Powder";}
    if ($file=~/.gr/)  {$xl="r (A)"; $yl="G(r)"; $n="PDF";}

    $data_x=""; $data_y="";
    open (I, "$outdir/$file");
    while ($line=<I>) {
      $line=~s/^\s*//; my ($x,$y)=split(/\s+/,$line);
      if (($x=~/[0-9]/) && ($y=~/[0-9]/)) {
        $data_x.=$x.",";
        $data_y.=$y.",";
      }
    }
    close I;
    $data_x=~s/$,//; $data_y=~s/$,//;
    
    print "<center><table><tr>\n";
    print "<th><h1>Plot of $title</h1></th></tr>\n<tr><td align=\"center\">";
    print "<div id=\"plot\" style=\"width:700px;height:450;\"></div>\n";

    print "<script>\n";
    print "  PLOT = document.getElementById('plot');\n";
    print "var trace1 = {x: [$data_x], y: [$data_y], type: 'lines+markers'};";
    print "var layout = {title:'$file', xaxis: {title: '$xl'}, yaxis: {title: '$yl'}};";
    print "Plotly.plot( PLOT, [trace1], layout);";
    print "</script></td</tr>\n";
  } else {
    print "<h3>File $file not found ..</h3>\n";
  }
}

