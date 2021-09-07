#! /usr/bin/env python3
# Script to decode UK domestic covid-19 QR codes
#
# Ref: https://github.com/nhsx/covid-pass-verifier/blob/91b3350fa974692f981630484876db5fc18db6e2/NHSCovidPassVerifier/Services/Repositories/QRDecoderService.cs#L61

import sys, base64, re

fmt = [
    { 'text': True, 'name':'Key' },
    { 'text': True, 'name':'Pay' },
    { 'text': False, 'name':'Sig' },
]
qr = sys.stdin.readline()
while qr[-1]<' ':
    qr = qr[:-1]
split = qr.split('.')
if len(split)!=3:
    print('QR code does not have three \'.\' separated parts', file=sys.stderr)
    sys.exit(1)
for idx in range(3):
    # We need to add padding if not a multiple of 4
    part = split[idx]
    while (len(part)%4):
        part += '='
    decoded = base64.urlsafe_b64decode(part)
    n = fmt[idx]['name']
    if fmt[idx]['text']:
        v = decoded.decode('utf-8')
    else:
        v = decoded.hex()
    print(f'{n}: {v}')
    if ('Pay'==n):
        # special payload decoding
        inp = v[1:]
        d = re.search('\d', inp)
        if not d:
            print('No digits in payload?', file=sys.stderr)
            sys.exit(1)
        c = re.search('[a-zA-Z]', inp)
        if not c:
            print('No characters in payload?', file=sys.stderr)
            sys.exit(1)
        exp = inp[d.start():c.start()]
        nam = inp[c.start():]
        print(f'\tname: {nam}')
        print('\tdate: 20', end='')
        sep = ['-','-',' ',':','']
        while len(exp)>=2:
            print(f'{exp[:2]}{sep[0]}', end='')
            exp = exp[2:]
            sep = sep[1:]
        print()
