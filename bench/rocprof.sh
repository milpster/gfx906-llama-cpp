#!/usr/bin/env bash
# Run rocprofv2 (ROCm 6.1-matched, see FINDINGS.md "PMU profiling") against a
# gfx906 workload. Usage mirrors rocprofv2:
#   ./rocprof.sh -i pmc-file.txt --plugin file -d OUT_DIR -- CMD [args...]
#   ./rocprof.sh --list-counters
# The archived stack matches the runtime in /opt/rocm-6.1.0 (build 60100);
# the 6.4.4 user-mode interposer must NOT be mixed in - it breaks device
# enumeration in children and faults the CP on kernel dispatch.
set -euo pipefail

HERE=$(cd "$(dirname "$0")" && pwd)
STACK=$HERE/rocprof-stack

export LD_LIBRARY_PATH="$STACK/lib:/opt/rocm-6.1.0/lib:${LD_LIBRARY_PATH:-}"
export HSA_OVERRIDE_GFX_VERSION=9.0.6
export HSA_XNACK=0
export AMD_LOG_LEVEL=0

exec "$STACK/bin/rocprofv2" "$@"
