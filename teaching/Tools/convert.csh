#!/bin/tcsh
foreach i (*.html)
  echo $i
  mv $i $i.orig
  ./Tools/convert.sed < $i.orig > $i
end
