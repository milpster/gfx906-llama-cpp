#!/usr/bin/env bash
# E132 trial window: GDN-norm port (upstream #28068 -> qwen4exp).
# Gates: /tmp/opencode/build-gdnnorm.OK exists AND port 8009 free.
# Then: stock lane e132b -> patched lane e132a (full user regime:
# PP16384 + fill 120k + TG1024 temp-0 sha + acc) -> PPL @120k ctx
# both sides (bench/perplexity-gdnnorm.sh). Mirror parity env per E119.6.
# Status: /tmp/opencode/run-window-e132.{DONE,FAIL}, log run-window-e132.log.
set -u
ROOT=/home/srcds/dev/uf3_rocm6.1_llama.cpp
WT=/home/srcds/dev/uf3-wt-gdn
OK=/tmp/opencode/build-gdnnorm.OK
FAILMARK=/tmp/opencode/build-gdnnorm.FAIL
LOG=/tmp/opencode/run-window-e132.log
exec >>"$LOG" 2>&1
echo "[e132] armed $(date)"

until [ -f "$OK" ]; do
    [ -f "$FAILMARK" ] && { echo "[e132] BUILD FAILED, aborting $(date)"; touch /tmp/opencode/run-window-e132.FAIL; exit 1; }
    sleep 30
done
echo "[e132] build OK $(date)"

while ss -ltn 2>/dev/null | grep -q ':8009 '; do sleep 30; done
echo "[e132] port 8009 free $(date); settling 60s"
sleep 60

cd "$ROOT"
export LLAMA_DFLASH_MIRROR_OUTPUT=1

rc_all=0

echo "[e132] stock lane start $(date)"
if env LANE=e132b BIN_DIR=$ROOT/build-dflash-novega C=250000 TS=35,20,45 SM=layer \
        CTV=q8_0 SPEC_TYPE=draft-dflash SPEC_N_MAX=4 NGRAM=0 FILL1=120000 FILL2=0 \
        TG_N=1024 EXTRA="--spec-draft-device ROCm0 --no-mmproj-offload" ./bench/lane-dflash.sh; then
    echo "[e132] stock lane DONE $(date)"
else
    echo "[e132] stock lane FAILED $(date)"; rc_all=1
fi

echo "[e132] patch lane start $(date)"
if env LANE=e132a BIN_DIR=$WT/build-gdnnorm C=250000 TS=35,20,45 SM=layer \
        CTV=q8_0 SPEC_TYPE=draft-dflash SPEC_N_MAX=4 NGRAM=0 FILL1=120000 FILL2=0 \
        TG_N=1024 EXTRA="--spec-draft-device ROCm0 --no-mmproj-offload" ./bench/lane-dflash.sh; then
    echo "[e132] patch lane DONE $(date)"
else
    echo "[e132] patch lane FAILED $(date)"; rc_all=1
fi

if [ "$rc_all" = 0 ]; then
    echo "[e132] PPL @120k start $(date)"
    if ./bench/perplexity-gdnnorm.sh; then
        echo "[e132] PPL DONE $(date)"
    else
        echo "[e132] PPL FAILED $(date)"; rc_all=1
    fi
fi

if [ "$rc_all" = 0 ]; then
    touch /tmp/opencode/run-window-e132.DONE
    echo "[e132] window complete $(date)"
else
    touch /tmp/opencode/run-window-e132.FAIL
    echo "[e132] window finished with failures $(date)"
fi
