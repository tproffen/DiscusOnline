#!/bin/tcsh
foreach i (*.html.orig)
  echo $i
#  mv $i $i.orig
  set out=`echo $i | sed 's/.html.orig/.html/' -`
  ./Tools/convert.sed < $i > $out
end
