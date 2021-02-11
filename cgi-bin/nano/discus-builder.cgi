#!/usr/bin/perl
#########################################################################
# Webinterface for DISCUS structure builder macros (see comments in
# macro files in 'mac' directory.
#
# (c) Thomas Proffen, 2010
#########################################################################

use CGI;
use Cwd;
use POSIX qw(strftime);
use Time::HiRes;

#########################################################################
# Directory on the server where files are created (rw for ALL)
# and URL where the pictures/text are then found.
#
# !! THESE NEED TO BE ADJUSTED FOR LOCAL INSTALLATION !! 
#
# The variables are:
# ------------------
#   $dishtml : This is the URL where the script output is found
#   $disdir  : This is the directory on the server for the DISCUS output
#   $cgidir  : This is the directory where 'discus.cgi' is installed
#   $find    : Path and name of 'find' program
#   $discus  : Path to discus
#   $jmol    : Location of Jmol on this server
#
#########################################################################

$find    = "/usr/bin/find";
$wwwroot = "/discus";
$disurl  = "http://tproffen.github.io/DiffuseCode";
$kupurl  = "http://tproffen.github.io/DiffuseCode";
$jmolurl = "http://www.jmol.org/";
$cgidir  = cwd;

$dishtml = "/discus/nano";
$discgi  = "/discus/cgi-bin/nano/discus-builder.cgi";
$plotcgi = "/discus/cgi-bin/nano/plotter.cgi";
$disdir  = "/var/www/html/DiscusOnline/nano";
$outdir  = "/var/www/html/DiscusOnline/nano/Output";
$wwwout  = "/discus/nano/Output/";
$dpath   = "/usr/local/bin/";


#########################################################################
# Here we set some global variables 
#########################################################################

$maxproc = 2;          # Maximum allowed number of DISCUS processes
$jsize   = 480;        # Size of Jmol window
$keep    = 2;          # Keep files for two days

#########################################################################

MAIN:
{
  $cgi = new CGI;
  $err=""; $el=0.0;

  $mac=$cgi->param('mac');
  system "$find $outdir -maxdepth 1 -ctime $keep -type f ".
         "-name $mac\\*.\\* -exec rm -f {} \\; ";

  $nproc = `ps | grep -c discus-builder.cgi -`;
  if ($nproc > $maxproc) {
    $err.="More than $maxproc DISCUS processes running. Try again later ..\n";
  } else {
    $form=&buildForm($mac);
    if ($form) {
      if ($cgi->param('P1')) {
        $id="$mac.".time();
        &runDiscus($mac);
      } else {
        $id="Defaults/$mac";
      }
    } else {
      $err="DISCUS macro <b>$cgidir/macros/$mac/main.mac</b> or ";
      $err.="<br><b>$cgidir/macros/$mac/default.mac</b> not found ..\n";
    }
  }

  # Creating HTML output
  
  print $cgi->header;
  print "<html><head>\n";
  print "<link href=\"$wwwroot/styles/discus.css\" ";
  print "      rel=\"stylesheet\"  type=\"text/css\">\n";
  print "<script src=\"$wwwroot/scripts/validate.js\"></script>\n";
  print "<script src=\"$wwwroot/scripts/JSmol.min.js\"></script>\n";
  print "<script type=\"text/javascript\">\n";
  print "  var Info = {\n";
  print "    width: $jsize,\n";
  print "    height: $jsize,\n";
  print "    use: \"HTML5\",\n";
  print "    j2sPath: \"$wwwroot/scripts/j2s\",\n";
  print "    console: \"jmolApplet0_infodiv\"\n";
  print "  }\n";
  print "</script>\n";
  print "</head>\n";
  print "<body>\n";
  print "<center>\n";
  print "<div class=\"builder\">\n";
  if ($err) {
    print "<h1>ERROR</h1>\n<p class=\"error\">$err</p>\n";
  } else {
    my $name=uc($mac);
    print "<table>\n";
    print "<tr><th colspan=\"2\"><h1>Builder: $name</h1>\n";

    print "<tr>\n";
    &printStructure();
    &printForm($form);
    print "</tr>\n";

    print "<tr>\n";
    &printInfo();
    print "</tr>\n";

    print "</table>\n";
    print "</td>\n";

  }
  print "</div>\n";
  print "<center>&nbsp;<br><a href='/discus/index.html'>Back to Discus Online Home</a></center>\n";
  print "</body></html>\n";
}

#------------------------------------------------------------------------------
sub runDiscus {

  my $start=Time::HiRes::time();
  
  my $cmd.="export LD_LIBRARY_PATH=$dpath:$LD_LIRARY_PATH;";
  $cmd.="umask 022;";
  $cmd.="cd $cgidir/macros/$mac;";
  $cmd.="$dpath/discus_suite -macro main.mac ";
  for (my $ip=0; $ip<$npar; $ip++) {$cmd.=$cgi->param("P$ip").",";}
  $cmd.="$outdir/$id";

  system "$cmd > $outdir/$id.log";
  my $end=Time::HiRes::time();
  $el=$end-$start;
}

#------------------------------------------------------------------------------
sub buildForm {

  if ((-r "$cgidir/macros/$mac/main.mac") &&
      (-r "$cgidir/macros/$mac/default.mac")) {
    $npar=0;
    $ret="<input type=\"hidden\" value=\"$mac\" name=\"mac\">\n";

    open (DEF,"$cgidir/macros/$mac/default.mac");
    while ($line=<DEF>) {
     if ($line=~/^\s*\@main/) {
       $line=~s/^\s*\@main\s+//; @def=split(/,/,$line);
     }
    }
    close DEF;
 
    open (MAC,"$cgidir/macros/$mac/main.mac");
    while ($line=<MAC>) {
      if ($line=~/^## Parameter/) {
        $line=~s/^## Parameter\s*//; $line=~s/\n*//g; $line=~s/\r*//g;
        ($par[$npar],$type[$npar],$label[$npar],
         $opt2[$npar],$opt3[$npar]) = split (/,/,$line);
        if ($type[$npar] eq 'real') {
          $ret.=&printNumber($npar,$label[$npar],$def[$npar],
                                 $opt2[$npar],$opt3[$npar],'');
        }
        elsif ($type[$npar] eq 'integer') {
          $ret.=&printNumber($npar,$label[$npar],$def[$npar],
                                 $opt2[$npar],$opt3[$npar],'I');
        }
        elsif ($type[$npar] eq 'file') {
          $ret.=&printFile($npar,$label[$npar],$opt2[$npar],$def[$npar]);
        }
        elsif ($type[$npar] eq 'select') {
          $ret.=&printSelect($npar,$label[$npar],$opt2[$npar],
                                   $opt3[$npar],$def[$npar]);
        }
        $npar++;
      }
      elsif ($line=~/^## Line/)  {$ret.="<hr>\n";}
      elsif ($line=~/^## Space/) {$ret.="<br>&nbsp;<br>\n";}
    }
    close MAC;

    $ret.=&printSubmit();
    return $ret;
  }
}

#------------------------------------------------------------------------------
sub printSubmit {

  my $ret;

  $ret ="<br><input type=\"submit\" value=\"RUN\" ";
  $ret.="onClick=\"this.value='Please wait ..';\" id=\"run\">\n";
  return $ret;
}
#------------------------------------------------------------------------------
sub printNumber {

  my ($p,$l,$def,$min,$max,$type)=@_;
  my $ret;

  $val=$cgi->param("P$p"); 
  unless ($val) {$val=$def;}
  $ret ="<b>$l</b>: <input name=\"P$p\" type=\"text\" value=\"$val\" ";
  $ret.="size=\"6\" onChange=\"valuevalidation(this,$min,$max,$def,";
  $ret.="'Allowed values between $min and $max !','$type');\"><br>\n";
  return $ret;
}

#------------------------------------------------------------------------------
sub printFile {

  my ($p,$l,$o,$d)=@_;
  my $ret;

  @files=glob("$cgidir/macros/$mac/$o");

  $val=$cgi->param("P$p");

  $ret ="<b>$l</b>: <select name=\"P$p\">\n";
  for ($i=0; $i<=$#files; $i++) {
    $fname=$files[$i]; $fname=~s/$cgidir\/macros\/$mac\///;
    $title=&getTitle($files[$i]);
    unless ($title) {$title=$fname;}
    $ret.="<option value=\"$fname\"";
    if ($val) {
      if($val eq $fname) {$ret.=" selected";}
    } else {
      if($d eq $fname) {$ret.=" selected";}
    }
    $ret.=">$title\n";
  }
  $ret.="</select><br>\n";
  return $ret;
}

#------------------------------------------------------------------------------
sub getTitle {

  my ($fname)=@_;
  my $ret='';

  open (F,$fname);
  while (<F>) {
    if ($_=~/title/) {
      $ret=$_; $ret=~s/^\s*title\s*//;
      $ret=~s/\n//;
    }
  }
  close F;
  return $ret;
}

#------------------------------------------------------------------------------
sub printSelect {

  my ($p,$l,$o1,$o2,$d)=@_;
  my $ret;

  @labels=split(/:/,$o1);
  @values=split(/:/,$o2);
  $val=$cgi->param("P$p");

  $ret ="<b>$l</b>: <select name=\"P$p\">\n";
  for ($i=0; $i<=$#labels; $i++) {
    $ret.="<option value=\"$values[$i]\"";
    if($val) {
      if($val eq $values[$i]) {$ret.=" selected";}
    } else {
      if($d eq $values[$i]) {$ret.=" selected";}
    }
    $ret.=">$labels[$i]\n";
  }
  $ret.="</select><br>\n";
  return $ret;
}

#------------------------------------------------------------------------------
sub printForm {

  my ($form) = @_;

  print "<td class=\"bcontrol\">\n";
  print "<form action=\"$discgi\" method=\"get\">\n";

  # Input form

  print "<h3>Nanobuilder input</h3>\n";
  print "$form\n";

  # Jmol controls
  
  print "<h3>Plot Controls</h3>\n";
  print "<p><b>Spin model</b></p>\n";
  print "<a href=\"javascript:Jmol.script(jmolApplet0,'spin on')\">Spin ON</a> -- \n";
  print "<a href=\"javascript:Jmol.script(jmolApplet0,'spin off')\">Spin OFF</a>\n";

  # Info part

  print "<h3>Results</h3>\n";
  if (-r "$outdir/$id.info") {
    open (F,"$outdir/$id.info"); while (<F>) {print $_;} close F;
  }
  print "</form></td>\n";
}

#------------------------------------------------------------------------------
sub printStructure {

  print "<td width=\"$jsize\" height=\"$jsize\">\n";
  if (-r "$outdir/$id.cif") {
     print "<script>\n";
     print "jmolApplet0 = Jmol.getApplet(\"jmolApplet0\", Info);\n";
     print "Jmol.script(jmolApplet0, \"load $wwwout/$id.cif; ";
     print "unitcell OFF; axes OFF; select *; center selected;\");\n";
     print "</script>\n";
  } else {
     print "<b>No structure file found</b>\n";
  }
  print "</td>\n";
}

#------------------------------------------------------------------------------
sub printInfo {

  my $cc ="onClick=\"window.open('$plotcgi?FILE=FFF&TITLE=TTT','WWW','";
     $cc.="menubar=no,";
     $cc.="toolbar=no,location=no,resizable=yes,scrollbars=yes,width=750,";
     $cc.="height=550')\"";

  print "<th colspan=\"2\">\n";
  print "<b>Files:</b>\n";
  if (-r "$outdir/$id.pow") {
    print "<a href=\"file.cgi?file=$id&type=pow\">Powder pattern</a> - ";
    $url=$cc; $url=~s/FFF/$id.pow/g; 
    $url=~s/TTT/Power Pattern/; 
    $url=~s/WWW/PlotPow/;
    print "[<a href=\"#\" $url>Plot</a>] -\n";
  }
  if (-r "$outdir/$id.gr") {
    print "<a href=\"file.cgi?file=$id&type=gr\">Pair Distribution Funtion</a> - ";
    $url=$cc; $url=~s/FFF/$id.gr/g; $url=~s/WWW/PlotGr/;
    $url=~s/TTT/Pair Distribution Function/; 
    print "[<a href=\"#\" $url>Plot</a>] -\n";
  }
  if (-r "$outdir/$id.nipl") {
    print "<a href=\"file.cgi?file=$id&type=nipl\">Diffuse Scattering</a> - ";
  }
  if (-r "$outdir/$id.cif") {
    print "<a href=\"file.cgi?file=$id&type=cif\">Structure (cif)</a> - ";
  }
  if (-r "$outdir/$id.log") {
    print "<a onClick=\"window.open('$wwwout/$id.log')\" ";
    print "href=\"#\">DISCUS logfile</a>\n";
  }
  my $ww=int(1.05*$jsize); $hh=int(1.3*$jsize);
  printf " -- <b>Calculation time:</b> <i>%.3f sec</i>\n", $el;
  print "</th>\n";
}

#----------------------------------------------------------------------------

sub include_file {
  my $fname = $_[0];

  if (open(INC,$fname)) {
    while ($line=<INC>) { print "$line"; }
  } else {
    print "<pre>[Error including $fname]</pre>\n";
  }
}

