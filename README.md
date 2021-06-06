# Decode COVID-19 QR data, aka decovid

This standalone python script provides a hacky decoder for UK/EU COVID-19 vaccine passport
data as stored in the 2D "QR" codes you present to travel authorities.

## Pre-requisites

Python 3.x

Some means to scan a QR code into a text file (I use the
[Cognex Barcode Scanner](https://play.google.com/store/apps/details?id=com.manateeworks.barcodescanners)
app on my mobile)

## Build

Nope.

## Run

`$ ./decovid.py < scanned-qr-code.txt`

NB: You may have to trim a space or two off the end of the text until it parses
