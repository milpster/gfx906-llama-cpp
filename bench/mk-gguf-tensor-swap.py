#!/usr/bin/env python3
"""Build a UD variant by swapping per-tensor quant types between GGUFs.

Used for UD-Q6_K_L v2: copy the production L file byte-exact, but take the
38 Q5_K tensors from an imatrix-quantized Q6_K donor (built with
llama-quantize --imatrix from the Q8_0 source). Keeps 93% of tensors
byte-identical to production so A/B deltas attribute to the 38 tensors.

Usage:
  mk-gguf-tensor-swap.py BASE.gguf DONOR.gguf OUT.gguf q5_k=q6_k [--dry-run]

Swap spec: source-type=target-type (ggml names, case-insensitive).
The donor tensor must exist with the same name/shape and the target type.
Rebuilds the tensor directory (types + offsets) and copies the KV section
verbatim from BASE.
"""
import struct
import sys
from gguf import GGMLQuantizationType, GGML_QUANT_SIZES

TYPE_BY_NAME = {t.name.lower(): t for t in GGMLQuantizationType}


def read_header(path):
    f = open(path, 'rb')
    magic, ver, n_tensors, n_kv = struct.unpack('<IIQQ', f.read(24))
    assert magic == 0x46554747, f'{path}: not a GGUF file'
    kv_start = f.tell()

    def rstr():
        n, = struct.unpack('<Q', f.read(8))
        return f.read(n)

    def skip_val(t):
        sizes = {0: 1, 1: 1, 2: 2, 3: 2, 4: 4, 5: 4, 6: 4, 7: 1, 10: 8, 11: 8, 12: 8}
        if t in sizes:
            f.read(sizes[t])
        elif t == 8:
            rstr()
        elif t == 9:
            it = struct.unpack('<I', f.read(4))[0]
            n, = struct.unpack('<Q', f.read(8))
            for _ in range(n):
                skip_val(it)
        else:
            raise ValueError(f'kv type {t}')

    alignment = 32
    for _ in range(n_kv):
        key = rstr().decode('utf-8', 'replace')
        t = struct.unpack('<I', f.read(4))[0]
        if key == 'general.alignment':
            alignment = struct.unpack('<I', f.read(4))[0]
        else:
            skip_val(t)
    kv_end = f.tell()

    tensors = []
    for _ in range(n_tensors):
        name = rstr().decode('utf-8', 'replace')
        nd = struct.unpack('<I', f.read(4))[0]
        dims = struct.unpack('<%dq' % nd, f.read(8 * nd))
        ttype = struct.unpack('<I', f.read(4))[0]
        off, = struct.unpack('<Q', f.read(8))
        ne = 1
        for d in dims:
            ne *= d
        block, tsize = GGML_QUANT_SIZES[GGMLQuantizationType(ttype)]
        nbytes = (ne + block - 1) // block * tsize
        tensors.append({'name': name, 'nd': nd, 'dims': dims, 'type': ttype,
                        'off': off, 'ne': ne, 'nbytes': nbytes})
    dir_end = f.tell()
    return f, tensors, alignment, kv_start, kv_end, dir_end, ver, n_kv


def main():
    base, donor_path, out, swap_spec, dry = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], len(sys.argv) > 5
    src_t, dst_t = swap_spec.lower().split('=')
    src = TYPE_BY_NAME[src_t]
    dst = TYPE_BY_NAME[dst_t]

    bf, bt, align, kv0, kv1, dir_end0, ver, n_kv_base = read_header(base)
    df, dt, dalign, _, _, ddir_end, _, _ = read_header(donor_path)
    donor_data_start = (ddir_end + dalign - 1) // dalign * dalign
    donor_by_name = {t['name']: t for t in dt}

    swapped = []
    out_tensors = []
    for t in bt:
        if t['type'] == int(src):
            d = donor_by_name[t['name']]
            assert d['type'] == int(dst), f"{t['name']}: donor type {d['type']} != {int(dst)}"
            assert d['ne'] == t['ne'], f"{t['name']}: shape mismatch"
            out_tensors.append({**t, 'type': int(dst), 'nbytes': d['nbytes'],
                                '_from': 'donor', '_donor_off': donor_data_start + d['off']})
            swapped.append(t['name'])
        else:
            out_tensors.append({**t, '_from': 'base'})
    assert swapped, f'no {src_t} tensors found in base'

    print(f'{len(swapped)} tensors {src_t}->{dst_t}:')
    for n in swapped:
        print(' ', n)

    # data section starts at the first aligned offset after the directory
    data_start = (dir_end0 + align - 1) // align * align
    # recompute offsets
    off = 0
    for t in out_tensors:
        off = (off + align - 1) // align * align
        t['new_off'] = off
        off += t['nbytes']
    total = data_start + off

    print(f'output size: {total/2**30:.2f} GiB')
    if dry:
        return

    with open(out, 'wb') as o:
        bf.seek(0)
        o.write(bf.read(dir_end0))            # magic+counts+KV+old dir (dir rewritten below)
        # rewrite tensor directory with new types/offsets (same order/names/dims)
        o.seek(0)
        o.write(struct.pack('<IIQQ', 0x46554747, ver, len(out_tensors),
                            (kv1 - kv0) and 0 or 0))  # placeholder, fixed next
        # simpler: rebuild whole header instead of patching - see below
    # NOTE: patching in place is fragile; rebuild header cleanly instead
    o = open(out, 'r+b')

    def wstr(s):
        b = s.encode('utf-8')
        o.write(struct.pack('<Q', len(b)) + b)

    o.seek(0)
    o.write(struct.pack('<IIQQ', 0x46554747, ver, len(out_tensors), n_kv_base))
    bf.seek(kv0)
    o.seek(24)
    o.write(bf.read(kv1 - kv0))               # KV section verbatim
    for t in out_tensors:                     # new tensor directory
        wstr(t['name'])
        o.write(struct.pack('<I', t['nd']))
        o.write(struct.pack('<%dq' % t['nd'], *t['dims']))
        o.write(struct.pack('<IQ', t['type'], t['new_off']))
    o.truncate(data_start)

    # data: base tensors from base, swapped from donor
    for t in out_tensors:
        o.seek(data_start + t['new_off'])
        if t['_from'] == 'donor':
            df.seek(t['_donor_off'])
            remaining = t['nbytes']
        else:
            bf.seek(t['off'] + data_start)
            remaining = t['nbytes']
        src_f = df if t['_from'] == 'donor' else bf
        while remaining > 0:
            chunk = src_f.read(min(1 << 24, remaining))
            assert chunk, f'short read on {t["name"]}'
            o.write(chunk)
            remaining -= len(chunk)
    o.close()
    print(f'wrote {out}')


if __name__ == '__main__':
    main()
