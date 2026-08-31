#!/usr/bin/env bash
# E50v2 precheck: verify the rig is idle before the e50v2 lane.
# Read-only: prints findings and stop instructions, NEVER kills anything.
# Exit 0 = clear to run the lane; exit 1 = busy.
set -u
cd "$(dirname "$(readlink -f "$0")")/.."

fail=0

echo "== llama-server processes =="
if pgrep -x llama-server > /dev/null; then
    pgrep -a -x llama-server
    echo "BUSY: a llama-server is running (likely your production server)."
    echo "  Stop it yourself (agent must never kill it), e.g.:"
    echo "    pkill -9 -x llama-server"
    echo "  then rerun this precheck."
    fail=1
else
    echo "none"
fi

echo
echo "== port 8014 =="
if ss -ltn 2>/dev/null | grep -q ':8014 '; then
    echo "BUSY: port 8014 is still bound (zombie server holds VRAM)."
    echo "  'HTTP server error' at lane start means exactly this."
    fail=1
else
    echo "free"
fi

echo
echo "== GPU summary =="
rocm-smi --showuse --showmemuse vram --showpids 2>/dev/null | head -20 || rocm-smi 2>/dev/null | head -20 || echo "rocm-smi unavailable"

echo
echo "== e50v2 binary =="
BIN=build-dflash-novega/bin/llama-server
if [ -x "$BIN" ]; then
    echo "$BIN present"
    if ldd "$BIN" 2>/dev/null | grep -q 'libhipblas.so.3'; then
        echo "WRONG LINKAGE: libhipblas.so.3 found (ROCm 7.x) - the lane will fail at start (D11/E31)."
        echo "  Rebuild build-dflash-novega with the six /opt/rocm-6.1.0 *_DIR pins."
        fail=1
    elif ldd "$BIN" 2>/dev/null | grep -q 'libhipblas.so.2'; then
        echo "linkage OK (libhipblas.so.2 = ROCm 6.1)"
    else
        echo "WARNING: could not confirm libhipblas.so.2 via ldd"
    fi
    HIPSO=build-dflash-novega/bin/libggml-hip.so.0
    if [ -f "$HIPSO" ]; then
        if grep -q gfx906 "$HIPSO"; then
            echo "HIP arch OK (gfx906 code object present)"
        else
            echo "WRONG ARCH: no gfx906 code object in $HIPSO (server dies at first kernel:"
            echo "  'ROCm error: invalid device function'). Reconfigure with -DAMDGPU_TARGETS=gfx906."
            fail=1
        fi
    fi
else
    echo "MISSING: $BIN - build build-dflash-novega first (GGML_CUDA_VEGA_TUNE=OFF)"
    fail=1
fi

echo
if [ "$fail" -ne 0 ]; then
    echo "PRECHECK: NOT CLEAR - resolve above, then rerun."
    exit 1
fi
echo "PRECHECK: CLEAR - run bench/e50v2-lane-200k.sh (~20 min)."
