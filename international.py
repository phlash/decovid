#! /usr/bin/env python3
#
# Decode a COVID-19 QR code text dump
# refs:
# CBOR: https://www.rfc-editor.org/rfc/rfc8949.html
# COSE: https://datatracker.ietf.org/doc/draft-ietf-cose-rfc8152bis-struct/15/

import sys, os
import zlib

# direct import of b45decode from:
# https://github.com/kirei/python-base45/blob/main/base45/__init__.py

"""
Base45 Data Encoding as described in draft-faltstrom-base45-02
"""

from typing import Union

BASE45_CHARSET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:"

def b45decode(s: Union[bytes, str]) -> bytes:
    """Decode base45-encoded string to bytes"""
    res = []
    try:
        if isinstance(s, str):
            buf = [BASE45_CHARSET.index(c) for c in s]
        else:
            buf = [BASE45_CHARSET.index(c) for c in s.decode()]
        buflen = len(buf)
        for i in range(0, buflen, 3):
            x = buf[i] + buf[i + 1] * 45
            if buflen - i >= 3:
                x = buf[i] + buf[i + 1] * 45 + buf[i + 2] * 45 * 45
                res.extend(list(divmod(x, 256)))
            else:
                res.append(x)
        return bytes(res)
    except (ValueError, IndexError, AttributeError):
        raise ValueError("Invalid base45 string")

def strip_qr(qr):
    # remove leading 'HC1:' if present, and trailing control chars (CR/LF)
    if qr.startswith('HC1:'):
        qr = qr[4:]
    while qr[-1]<' ':
        qr = qr[:-1]
    return qr

def get_cbor(qr):
    # reverse the encoding specified by EU e-Health Network (eHN)
    # un-base45 from QR text
    cmp = b45decode(qr)
    # check first byte is 0x78 indicating deflate compression
    if cmp[0] != 0x78:
        print('oops: not compressed with deflate/zlib?')
        return None
    return zlib.decompress(cmp)

def decode_cbor(pfx, cbor, pos, isCOSE):
    print(pfx,end='')
    # decode one CBOR data item
    # https://www.rfc-editor.org/rfc/rfc8949.html
    # grab the initial byte
    ib = cbor[pos]
    pos += 1
    # decode major type
    maj = (ib >> 5) & 0x7
    # decode value arg
    val = ib & 0x1f
    # grab additional value bytes if required
    if val>23 and val<28:
        cnt = 1<<(val-24)
        val = 0
        while cnt>0:
            val <<= 8
            val |= cbor[pos]
            pos += 1
            cnt -= 1
    elif 31==val:
        # TODO terminate indefinite length string/array/map
        print('oops: val=31')
        return pos
    # process major type
    if 0==maj:
        # unsigned int, nothing to do
        print('int:%d'%(val,))
    elif 1==maj:
        # negative int, subtract from -1
        print('neg:%d'%(-1-val,))
    elif 2==maj:
        # byte string, grab 'em
        byts = cbor[pos:pos+val]
        pos += val
        print('hex:%s'%(byts.hex(),))
        if isCOSE:
            # COSE_Sign1 byte strings always contain more CBOR, we recurse..
            decode_cbor(pfx+' (cose) ',byts,0,False)
    elif 3==maj:
        # text string, grab 'em
        byts = cbor[pos:pos+val]
        pos += val
        print('txt:%s'%(byts.decode('utf-8'),))
    elif 4==maj:
        # array (counted), let's recurse..
        print('arr:%d'%(val,))
        for i in range(0,val):
            # array entry 3 in COSE_Sign1 is the raw signature
            pos = decode_cbor(pfx+'  ', cbor, pos, isCOSE and i<3)
    elif 5==maj:
        # map (counted), let's recurse..
        print('map:%d'%(val,))
        for i in range(0,val):
            pos = decode_cbor(pfx+'  (key) ', cbor, pos, isCOSE);
            pos = decode_cbor(pfx+'  (val) ', cbor, pos, isCOSE);
    elif 6==maj:
        # tagged item, let's recurse for the item (and indicate COSE_Sign1)
        cs1 = (18==val)
        if cs1:
            print('tag:%d (cose)'%(val,))
        else:
            print('tag:%d'%(val,))
        pos = decode_cbor(pfx+'  (item) ', cbor, pos, cs1)
    elif 7==maj:
        # float/simple and 'stop' marker
        print('(float/simple) TODO')
    return pos

if __name__ == '__main__':
    qr = sys.stdin.readline()
    strp=strip_qr(qr)
    cbor = get_cbor(strp)
    pos = 0
    while pos<len(cbor):
        pos = decode_cbor('', cbor, pos, False)

