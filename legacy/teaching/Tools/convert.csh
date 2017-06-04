#!/bin/tcsh
foreach i (*.html)
  echo $i
  rm -f $i
  ./Tools/convert.sed < $i.orig > $i
end
