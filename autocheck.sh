#!/bin/bash

lines=`ls "$1" | grep pdf$`

while read -r pdf;
do
	echo -e "\n------------ $pdf ---------------\n" > "$pdf.out"
    time python pdftools.py "$1/$pdf" &>> "$pdf.out"
    #gprof ./pdfmanager gmon.out >> "$pdf.out"
	echo -e "\n--------------------------------------\n\n" >> "$pdf.out"
done <<< "$lines"

exit 0

