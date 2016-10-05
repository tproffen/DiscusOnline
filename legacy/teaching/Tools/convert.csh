#!/bin/tcsh
foreach i (*.html)
  echo $i
  mv $i $i.orig
  ./convert.sed < $i.orig > $i
end
