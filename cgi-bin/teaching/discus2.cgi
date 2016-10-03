#!/usr/bin/perl
#########################################################################
# This is the generic interface to DISCUS and KUPLOT
# Version: 2.0
#
# (c) Thomas Proffen, 2003
#########################################################################

use CGI;
use POSIX qw(strftime);

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
#   $discus  : The directory where the DISCUS/KUPLOT executables are
#   $grfont  : Location of PGPLOT font grfont.dat used by KUPLOT
#
#   $disurl  : URL pointing to the DISCUS homepage (leave the default)
#   $kupurl  : URL pointing to the KUPLOT homepage (leave the default)
#
#   $path    : If $PATH not defined, add path to UNIX commands here
#   $find    : Path and name of 'find' program
#
#########################################################################

#------------------------------------------------------------------------
# MSU
#------------------------------------------------------------------------

$dishtml="/old/teaching/Output";
$discgi ="/cgi-bin/discus2.cgi";
$disdir ="/var/www/lighttpd/old/teaching/Output";
$cgidir ="/var/www/lighttpd/cgi-bin/";
$discus ="/usr/local/bin";
$grfont ="/usr/local/pgplot/grfont.dat";
$disurl ="http://www.pa.msu.edu/cmp/billinge-group/discus/discus.html";
$kupurl ="http://www.pa.msu.edu/cmp/billinge-group/discus/kuplot.html";
$find   = "/usr/bin/find";

#########################################################################
# Here we set some global variables 
#########################################################################

$maxproc = 5;          # Maximum allowed number of DISCUS processes
$keep = 3;             # Number of days to keep output files in cache

#########################################################################

MAIN:
{
  # Init CGI object
  $cgi = new CGI;

  # Read in all variables set by the form
  &CGI::ReadParse(*input);
  $startup=!$input{'P1'};
  $form=&buildForm();

  # Create parameter list for DISCUS call
  # Remove all blanks from each parameter, 
  # then add the leading blank to each parameter

  $param = "";
  $bname = $input{'script'};
  foreach $key (sort keys(%input)) {
      if ($key =~ /P/) {
          $wert  =   "$input{$key} ";
          $wert  =~tr/\ //d;
          $param .= " ";
          $param .=  $wert;
          $bname .= "_$input{$key}";
      }
  } 

  # remove all blanks from the filename

  $bname =~ tr/\ //d;

  # Run the script specified in the hidden tag if file does not
  # yet exist and perform a bit of basic error checking,
  # "bname" may contain only "a-Z0-9_.-"

  if ( $bname !~ /^[\w.-]+$/ && $bname !~ /^[teach_]+$/ && $bname !~ /\053/ ) { 
       open (ERR, "> $disdir/$bname.err");
       print ERR "<p><h2>Wrong characters in input fields !</h2>";
       print ERR "<p>You may only enter numbers, letters and the + and - sign.";
       close(ERR);
  }
  else {
    if (! -r "$disdir/$bname.gif") {
      $cache="";
      $nproc = `ps | grep -c discus.cgi -`;
      if ($nproc > $maxproc) {
          open (ERR, "> $disdir/$bname.err");
          print ERR "\nThe upper limit of $maxproc users has been exceeded !\n";
          print ERR "<br>Try again later ...\n";
          close (ERR);
      }
      else {
        unless ($startup) {
          $cmd = "cd $disdir; umask 022;
  	          export PATH=/bin:/usr/bin:$discus; export PGPLOT_FONT=$grfont;
                  $cgidir/mac/$input{'script'} $param";
	  system "$cmd";
          $cret=strftime "%d. %b %Y at %I:%M %p", localtime();
          $cache ="<font size=\"-1\">\n";
          $cache.="Created: <i>$cret</i>\n";
          $cache.="</font>\n";
        } 
      } 
    }
    else {
      ($dev,$ino,$mode,$nlink,$uid,$gid,$rdev,$size,
       $atime,$mtime,$ctime,$blksize,$blocks)=stat("$disdir/$bname.gif");
      $modt=strftime "%d. %b %Y at %I:%M %p", localtime($mtime);
      $acct=strftime "%d. %b %Y at %I:%M %p", localtime($atime);
      $cache ="<font size=\"-1\">\n";
      $cache.="Created: <i>$modt</i>, Last access: <i>$acct</i>\n";
      $cache.="</font>\n";
    }
  }

  # Creating HTML output
  
  print $cgi->header;
  print "<html>\n<head>\n";
  print "<title>$title</title>\n";
  print "<script language=\"JavaScript\">\n";
  print "  wait = new Image();\n";
  print "  wait.src = \"$dishtml/wait.gif\"\n";;
  print "  function message() {document.image.src=\"$dishtml/wait.gif\";}\n";
  print "</script></head>\n";

  print '<body bgcolor="#'."$page_bg".'" text="#0A3E00"'."\n";
  print '    link="#1A4D73" vlink="#1E5986" alink="#CC0005"'."\n";
  print '    topmargin="0" leftmargin="0" rightmargin="0"'."\n";
  print '    marginwidth="0" marginheight="0">'."\n";

  print "<table border=0 cellpadding=10 height=100% \n";
  print "       width=100% bgcolor=\"#$tab_bg\">\n";
  print "<tr>\n";
  print "<td colspan=2 height=5% align=center bgcolor=\"#$head_bg\">\n";
  print "<b>Interactive Tutorial about Diffraction</b><br>\n";
  print "<b><font color=\"#$head_fg\" size=\"+2\">";
  print "$title</font></b>\n";
  print "</td>\n";
  print "</tr>\n";
  print "<tr>\n";

  if ($fside eq 'left') {
    &printForm;
    &printImage;
  } else {
    &printImage;
    &printForm;
  }

  print "</tr>\n";
  print "<tr>\n";
  print "<td valign=bottom height=5% align=right ";
  print " colspan=2 bgcolor=\"#$head_bg\">\n";
  print "Created using the programs <a href=\"$disurl\"> DISCUS</a> and\n";
  print "<a href=\"$kupurl\"> KUPLOT</a>\n";
  print "</td></tr></table>\n";

  # Close the document cleanly.
  print $cgi->end_html;

  # GIF,PS files to clean up ?
  system "$find $disdir -ctime +$keep -name \\*.gif -exec rm -f {} \\; ";
  system "$find $disdir -ctime +$keep -name \\*.ps  -exec rm -f {} \\; ";
  system "$find $disdir -ctime +$keep -name \\*.err -exec rm -f {} \\; ";
}

#------------------------------------------------------------------------------

sub buildForm {

  my $ret;

  if (open(COL,"$cgidir/mac/defaults.form")) {
    while($line=<COL>) {
      chop($line); chop($line);
      if ($line=~/^page_bg=/) { $page_bg=$line; $page_bg=~s/page_bg=//; }
      if ($line=~/^form_bg=/) { $form_bg=$line; $form_bg=~s/form_bg=//; }
      if ($line=~/^tab_bg=/)  { $tab_bg=$line; $tab_bg=~s/tab_bg=//; }
      if ($line=~/^head_bg=/) { $head_bg=$line; $head_bg=~s/head_bg=//; }
      if ($line=~/^head_fg=/) { $head_fg=$line; $head_fg=~s/head_fg=//; }
      if ($line=~/^gsize=/)   { $gsize=$line; $gsize=~s/gsize=//; }
      if ($line=~/^fside=/)   { $fside=$line; $fside=~s/fside=//; }
    }
    close COL;
  } else {
    $page_bg="FFFFFF";
    $form_bg="FFFFFF";
    $tab_bg="CCCCCC";
    $head_bg="CCCCCC";
    $head_fg="990000";
    $gsize=1.0;
    $fside="left";
  }

  if (open(FORM,"$cgidir/mac/$input{'script'}.form")) {
    $ret.="<form method=\"get\" name=\"discus\"\n";
    $ret.="      action=\"$discgi\">\n";
    $ret.="<input type=\"hidden\" name=\"script\" ";
    $ret.="value=\"$input{'script'}\">\n";

    my $pmax=0;
    while($line=<FORM>) {
      chop($line); chop($line);
      if ($line=~/^title=/) { $title=$line; $title=~s/title=//; }
     
      # horizontal line
      if ($line=~/^HR/) {$ret.="\n<hr>\n";}
     
      # gap
      if ($line=~/^P/) {$ret.="\n<br>\n";}
     
      # input field
      if ($line=~/^text/) {
        $line=~s/text=//;
        @para=split(/,/,$line);
        $ret.="<b>$para[3]:</b>\n";
        unless ($input{"P$para[0]"}) {$input{"P$para[0]"}=$para[2];}
	$value=$input{"P$para[0]"};
        $ret.="<input type=\"text\" name=\"P$para[0]\" value=\"$value\"";
        $ret.=" size=\"$para[1]\"><br>\n";
        $pmax=max($pmax,$para[0]);
      }
      
      # radio button field
      if ($line=~/^radio/) {
        $line=~s/radio=//;
        @para=split(/,/,$line);
        $ret.="<b>$para[3]:</b><br>\n";
        unless ($input{"P$para[0]"}) {$input{"P$para[0]"}=$para[2];}
	$value=$input{"P$para[0]"};
        for (my $i=1; $i<=$para[1]; $i++) {
          $line=<FORM>; chop($line); chop($line);
          @check=split(/,/,$line);
          $ret.="$check[0] \n";
          $ret.="<input type=\"radio\" name=\"P$para[0]\" value=\"$check[1]\"";
          if ($check[1] eq $value) {$ret.=" checked";}
          $ret.="><br>\n";
        }
        $pmax=max($pmax,$para[0]);
      }
      
      # Run buttons
      if ($line=~/^submit/) {
        $ret.="<input type=\"submit\" value=\"  RUN  \" name=\"run\"\n";
        $ret.="       OnClick=message()>\n";
      }
    }
    $pmax++;
    $ret.="<input type=\"hidden\" name=\"P$pmax\" value=\"$gsize\">\n";
    unless ($input{"P$pmax"}) {$input{"P$pmax"}=$gsize;}
    $ret.="</form>\n";
    close FORM;
  } else {
    $ret=0;
  }

  return $ret;
}

#------------------------------------------------------------------------------

sub printImage {

  print "<td valign=middle align=center bgcolor=\"#$page_bg\">\n";
  if (-r "$disdir/$bname.err") 
    {
      print "<p align=center>\n";
      print "<font color=\"#$head_fg\" size=\"+1\">\n";
      print "<b>Error occured</b></font>\n";
      open (ERR, "< $disdir/$bname.err");
      while (<ERR>) {print "$_";}
      close (ERR);
      print "<p align=right>\n";
      print "[<a href=\"javascript:window.close()\">Close window</a>]</p>\n";
      unlink ("$disdir/$bname.err");
    }
  else
    {
      unless ($startup) {
        print "<img name=\"image\" src=\"$dishtml/$bname.gif\" vspace=5>\n";
        print "</center>\n<p align=\"right\">";
        if (-r "$disdir/$bname.ps") {
          print "[<a href=\"$dishtml/$bname.ps\">Postscript</a>]\n";
        }
      
        print "[<a href=\"javascript:window.close()\">Close window</a>]<br>\n";
        print "$cache</p>\n";
      } else {
        print "<img name=\"image\" src=\"$dishtml/startup.gif\" vspace=5>\n";
        print "</center>\n";
      }
    }
  print "</td>\n";
}

#------------------------------------------------------------------------------

sub printForm {

  print "<td valign=top align=right \n";
  print "    bgcolor=\"#$form_bg\" width=\"25%\">\n";
  print "<p>\n$form\n</td>\n";
}

#------------------------------------------------------------------------------

sub max {
  my ($a,$b)=@_;

  if ($a >= $b) { return $a; }
  else          { return $b; }
}
