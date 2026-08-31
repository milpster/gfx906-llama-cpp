#!/usr/bin/env python3
"""Aggregate rocprof PMC results by kernel class and derive gfx906 pipe metrics.

Usage: analyze-pmc.py CSV_DIR...   (each dir contains pmc_*/results_*.csv)

Counter groups (see pmc-a/b/c.txt in /tmp/opencode/rocprof, recipes in FINDINGS.md):
  A: GRBM_COUNT, GRBM_GUI_ACTIVE, SQ_ACTIVE_INST_VALU, SQ_INSTS_VALU, SQ_WAVES
  B: SQ_INSTS_LDS, SQ_INSTS_SALU, SQ_INSTS_SMEM, SQ_LDS_BANK_CONFLICT
  C: SQ_INSTS_VMEM_RD, SQ_INSTS_VMEM_WR

Derived (ROCm formulas, SIMD_NUM=4):
  VALUBusy  = 100*SQ_ACTIVE_INST_VALU*4/SIMD_NUM/GRBM_GUI_ACTIVE
  GPUBusy   = 100*GRBM_GUI_ACTIVE/GRBM_COUNT
"""
import csv
import glob
import re
import sys
from collections import defaultdict

SIMD_NUM = 4

CLASSES = [
    (r"^void mul_mat_q<", "mul_mat_q (MMQ GEMM)"),
    (r"^void quantize_mmq_q8_1<", "quantize_mmq_q8_1"),
    (r"fattn|flash_attn", "flash_attn"),
    (r"gated_delta_net|ssm_conv|ssm_scan|l2_norm_f32<32", "gdn_recurrent"),
    (r"rms_norm", "rms_norm"),
    (r"cpy_", "copies"),
    (r"k_get_rows", "get_rows"),
    (r"op_add|op_mul|op_silu|op_sigmoid|op_softplus|unary|bin_bcast|gated_op", "elementwise"),
]


def classify(name):
    for pat, cls in CLASSES:
        if re.search(pat, name):
            return cls
    return None


def main():
    dirs = sys.argv[1:]
    agg = defaultdict(lambda: defaultdict(float))  # (gpu, cls, metric) -> sum
    kernels_seen = defaultdict(int)

    for d in dirs:
        for path in sorted(glob.glob(d + "/pmc_*/results_*.csv")):
            with open(path, newline="") as f:
                rd = csv.DictReader(f)
                for row in rd:
                    name = row["Kernel_Name"]
                    cls = classify(name)
                    if cls is None:
                        continue
                    key = (row["GPU_ID"], cls)
                    for m, v in row.items():
                        if m in ("Kernel_Name", "Dispatch_ID", "Queue_ID", "PID", "TID"):
                            continue
                        try:
                            agg[key][m] += float(v)
                        except (TypeError, ValueError):
                            pass
                    kernels_seen[name] += 1

    metrics = ["GRBM_COUNT", "GRBM_GUI_ACTIVE", "SQ_ACTIVE_INST_VALU", "SQ_INSTS_VALU",
               "SQ_WAVES", "SQ_INSTS_LDS", "SQ_INSTS_SALU", "SQ_INSTS_SMEM",
               "SQ_LDS_BANK_CONFLICT", "SQ_INSTS_VMEM_RD", "SQ_INSTS_VMEM_WR"]

    classes = sorted({cls for (_, cls) in agg})
    gpus = sorted({gpu for (gpu, _) in agg})

    for gpu in gpus:
        tot = agg[(gpu, "TOTAL")] if (gpu, "TOTAL") in agg else None
        busy_all = sum(agg[(gpu, c)].get("GRBM_GUI_ACTIVE", 0) for c in classes)
        print(f"\n=== GPU_ID {gpu} ===")
        print(f"{'kernel class':28s} {'busy%':>6s} {'VALUb%':>7s} {'VALU/LDS':>8s} "
              f"{'VALU/SALU':>9s} {'VALU/SMEM':>9s} {'bcyc/1kc':>9s} {'VMEMrd':>9s}")
        for c in classes:
            a = agg[(gpu, c)]
            gui = a.get("GRBM_GUI_ACTIVE", 0)
            if gui <= 0:
                continue
            valu = a.get("SQ_INSTS_VALU", 0)
            valub = 100.0 * a.get("SQ_ACTIVE_INST_VALU", 0) * 4 / SIMD_NUM / gui
            lds, salu, smem = a.get("SQ_INSTS_LDS", 0), a.get("SQ_INSTS_SALU", 0), a.get("SQ_INSTS_SMEM", 0)
            bc = a.get("SQ_LDS_BANK_CONFLICT", 0)
            vrd = a.get("SQ_INSTS_VMEM_RD", 0)
            share = 100.0 * gui / busy_all if busy_all else 0
            print(f"{c:28s} {share:6.1f} {valub:7.1f} "
                  f"{(valu/lds if lds else 0):8.2f} {(valu/salu if salu else 0):9.2f} "
                  f"{valu/smem if smem else 0:9.2f} {1000.0*bc/gui:9.2f} {(vrd/valu if (vrd and valu) else 0):9.3f}")
        # absolute VALU issue rate needs cycles->time; print raw busy cycles
        print(f"{'(busy cycles, all classes)':28s} {busy_all:.3e}")


if __name__ == "__main__":
    main()
