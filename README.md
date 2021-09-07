# Decode COVID-19 QR data, aka decovid

This standalone python script provides a hacky decoder for UK/EU COVID-19 vaccine passport
data as stored in the 2D "QR" codes you present to travel authorities.

It also provides a decoder for domestic COVID-19 PASS "QR" codes you present at domestic events.

## Pre-requisites

Python 3.x

Some means to scan a QR code into a text file (I use the
[Cognex Barcode Scanner](https://play.google.com/store/apps/details?id=com.manateeworks.barcodescanners)
app on my mobile), or the excellent [ZBar Tools](https://github.com/mchehab/zbar) - available as a
standard package on my Debian stable system.

## Build

Nope.

## Run

International (aka UK/EU) passports, any ONE of:
```bash
$ zbarimg -q --raw |./international.py      (for previously captured image files)
$ zbarcam -q --raw |./international.py      (for live camera decoding)
$ ./international.py < scanned-qr-code.txt  (for previously decoded QR text)
```

Domestic COVID-19 PASSes, any ONE of:
```bash
$ zbarimg -q --raw |./domestic.py      (for previously captured image files)
$ zbarcam -q --raw |./domestic.py      (for live camera decoding)
$ ./domestic.py < scanned-qr-code.txt  (for previously decoded QR text)
```
