#!/usr/bin/env bash
# One bisect step: build current HEAD into build-bisect, run 2200-tok PP,
# verdict by throughput. Exit 0=good, 1=bad, 125=skip (build/launch fail).
set -u
cd /home/srcds/dev/uf2_rocm6.1_llama.cpp
LOG=/tmp/bisect-step.log
PORT=8015

if ! ROCM_PATH=/opt/rocm-6.1.0 cmake -S . -B build-bisect -DCMAKE_BUILD_TYPE=Release \
    -DGGML_HIP=ON -DAMDGPU_TARGETS=gfx906 -DGPU_TARGETS=gfx906 \
    -DGGML_HIP_GRAPHS=ON -DGGML_HIP_NO_VMM=ON -DGGML_CUDA_FORCE_MMQ=ON \
    -DGGML_LTO=OFF -DGGML_VULKAN=ON \
    -DCMAKE_HIP_FLAGS="-ffast-math -fno-math-errno" \
    -DCMAKE_EXE_LINKER_FLAGS="-L/opt/rocm-6.1.0/lib -L/home/srcds/rocm-gfx906-xnack/lib" \
    -DCMAKE_SHARED_LINKER_FLAGS="-L/opt/rocm-6.1.0/lib -L/home/srcds/rocm-gfx906-xnack/lib" \
    -DCMAKE_HIP_COMPILER=/opt/rocm-6.1.0/lib/llvm/bin/clang > "$LOG" 2>&1; then
  echo "SKIP: cmake configure failed"; exit 125
fi
if ! cmake --build build-bisect --target llama-server -j16 >> "$LOG" 2>&1; then
  echo "SKIP: build failed"; exit 125
fi

SRV_LOG=/tmp/bisect-srv.log
( setsid env PORT=$PORT bench/bisect/launch-min.sh > "$SRV_LOG" 2>&1 & )
for i in $(seq 1 30); do
  curl -sf -m 2 http://127.0.0.1:$PORT/health >/dev/null 2>&1 && break
  sleep 8
done
if ! curl -sf -m 3 http://127.0.0.1:$PORT/health >/dev/null; then
  pkill -9 -f "port $PORT" 2>/dev/null
  echo "SKIP: server failed to start"; exit 125
fi

TPS=$(python3 - <<'EOF'
import json, urllib.request, time, re, sys
BASE="http://127.0.0.1:8015"
filler=" ".join(f"The {w} archive records event {i:05d} with measure {i*7%997:03d}." for i,w in enumerate(["red","blue","green"]*800))
try:
    toks=json.loads(urllib.request.urlopen(urllib.request.Request(BASE+"/tokenize",data=json.dumps({"content":filler}).encode(),headers={"Content-Type":"application/json"}),timeout=60).read())["tokens"][:2200]
    p={"prompt":toks,"n_predict":2,"temperature":0,"cache_prompt":False,"id_slot":0,"stream":False}
    t0=time.time()
    urllib.request.urlopen(urllib.request.Request(BASE+"/completion",data=json.dumps(p).encode(),headers={"Content-Type":"application/json"}),timeout=600).read()
    dt=time.time()-t0
    print(f"{2200/dt:.0f}")
except Exception as e:
    print("FAIL", file=sys.stderr); sys.exit(1)
EOF
) || { pkill -9 -f "port $PORT" 2>/dev/null; echo "SKIP: bench failed"; exit 125; }

pkill -9 -f "port $PORT" 2>/dev/null
sleep 4
echo "TPS=$TPS"
if [ "$TPS" -ge 200 ]; then echo "GOOD"; exit 0; fi
if [ "$TPS" -lt 200 ]; then echo "BAD"; exit 1; fi
exit 125
