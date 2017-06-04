#!/bin/sed -f

/<body/,/>/{s/.//g}

s/<\/head>/<link href=\"\/styles\/discus.css\" rel=\"stylesheet\" type=\"text\/css\">\n<\/head>\n<body>/

