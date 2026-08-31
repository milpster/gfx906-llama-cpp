#!/usr/bin/env bash
# Rebuild the full rocprofiler 6.4.4 tool tree in /tmp from the ROCm apt repo
# (download-only, nothing installed) if bench/rocprof-stack becomes unusable
# because the system /opt/rocm-6.4.4 partial install changed or disappeared.
set -euo pipefail

OUT=${1:-/tmp/opencode/rocprof/root}
mkdir -p "$OUT"
cd "$(dirname "$OUT")"

apt-get download rocprofiler rocprofiler-plugins rocprofiler-sdk comgr hsa-amd-aqlprofile
for d in *.deb; do dpkg-deb -x "$d" "$(dirname "$OUT")/root_pkg/"; done
# resulting tree: root_pkg/opt/rocm-6.4.4 - use it directly or refresh
# bench/rocprof-stack from it (see bench/rocprof.sh for which parts matter)
echo "extracted to $(dirname "$OUT")/root_pkg/opt/rocm-6.4.4"
