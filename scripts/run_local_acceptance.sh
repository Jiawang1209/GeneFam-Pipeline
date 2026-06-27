#!/usr/bin/env bash

set -u

PYTHON_BIN=${PYTHON_BIN:-python}
CONDA_ENV=${CONDA_ENV:-GeneFamilyFlow}
RELEASE_OUTDIR=${RELEASE_OUTDIR:-results/release_checks}
PUBLICATION_OUTDIR=${PUBLICATION_OUTDIR:-results/publication_report_audit}
REPORT_INDEX_OUTDIR=${REPORT_INDEX_OUTDIR:-results/report_index_audit}
QUICKSTART_OUTDIR=${QUICKSTART_OUTDIR:-results/quickstart}
DELIVERY_OUTDIR=${DELIVERY_OUTDIR:-results/delivery_bundle}
ACCEPTANCE_OUTDIR=${ACCEPTANCE_OUTDIR:-results/local_acceptance}

echo "[GeneFam] Running release gate into ${RELEASE_OUTDIR}"
"$PYTHON_BIN" bin/genefam/run_release_checks.py --outdir "$RELEASE_OUTDIR"
release_status=$?
publication_status=$("$PYTHON_BIN" - "$RELEASE_OUTDIR/release_checks.tsv" <<'PY'
import csv
import sys
from pathlib import Path

path = Path(sys.argv[1])
if not path.exists():
    raise SystemExit(1)
with path.open("r", encoding="utf-8", newline="") as handle:
    for row in csv.DictReader(handle, delimiter="\t"):
        if row.get("check") == "publication report audit":
            raise SystemExit(int(row.get("exit_code") or 1))
raise SystemExit(1)
PY
)
publication_status=$?
standard_report_index_status=$("$PYTHON_BIN" - "$RELEASE_OUTDIR/release_checks.tsv" <<'PY'
import csv
import sys
from pathlib import Path

path = Path(sys.argv[1])
if not path.exists():
    raise SystemExit(1)
with path.open("r", encoding="utf-8", newline="") as handle:
    for row in csv.DictReader(handle, delimiter="\t"):
        if row.get("check") == "standard report index audit":
            raise SystemExit(int(row.get("exit_code") or 1))
raise SystemExit(1)
PY
)
standard_report_index_status=$?
wgd_publication_status=$("$PYTHON_BIN" - "$RELEASE_OUTDIR/release_checks.tsv" <<'PY'
import csv
import sys
from pathlib import Path

path = Path(sys.argv[1])
if not path.exists():
    raise SystemExit(1)
with path.open("r", encoding="utf-8", newline="") as handle:
    for row in csv.DictReader(handle, delimiter="\t"):
        if row.get("check") == "WGD publication report audit":
            raise SystemExit(int(row.get("exit_code") or 1))
raise SystemExit(1)
PY
)
wgd_publication_status=$?
wgd_report_index_status=$("$PYTHON_BIN" - "$RELEASE_OUTDIR/release_checks.tsv" <<'PY'
import csv
import sys
from pathlib import Path

path = Path(sys.argv[1])
if not path.exists():
    raise SystemExit(1)
with path.open("r", encoding="utf-8", newline="") as handle:
    for row in csv.DictReader(handle, delimiter="\t"):
        if row.get("check") == "WGD report index audit":
            raise SystemExit(int(row.get("exit_code") or 1))
raise SystemExit(1)
PY
)
wgd_report_index_status=$?

echo "[GeneFam] Running quickstart handoff into ${QUICKSTART_OUTDIR}"
"$PYTHON_BIN" bin/genefam/run_quickstart.py \
  --conda-env "$CONDA_ENV" \
  --outdir "$QUICKSTART_OUTDIR"
quickstart_status=$?

echo "[GeneFam] Refreshing delivery bundle into ${DELIVERY_OUTDIR}"
"$PYTHON_BIN" bin/genefam/run_delivery_bundle.py \
  --release-checks "$RELEASE_OUTDIR/release_checks.tsv" \
  --objective-audit results/objective_audit/objective_audit.tsv \
  --readiness results/readiness/command_readiness.tsv \
  --quickstart "$QUICKSTART_OUTDIR/quickstart_summary.tsv" \
  --outdir "$DELIVERY_OUTDIR"
delivery_status=$?

echo "[GeneFam] Writing local acceptance summary into ${ACCEPTANCE_OUTDIR}"
"$PYTHON_BIN" bin/genefam/write_local_acceptance_summary.py \
  --release-status "$release_status" \
  --publication-status "$publication_status" \
  --standard-report-index-status "$standard_report_index_status" \
  --wgd-publication-status "$wgd_publication_status" \
  --wgd-report-index-status "$wgd_report_index_status" \
  --quickstart-status "$quickstart_status" \
  --delivery-status "$delivery_status" \
  --release-outdir "$RELEASE_OUTDIR" \
  --publication-outdir "$PUBLICATION_OUTDIR" \
  --report-index-outdir "$REPORT_INDEX_OUTDIR" \
  --quickstart-outdir "$QUICKSTART_OUTDIR" \
  --delivery-outdir "$DELIVERY_OUTDIR" \
  --outdir "$ACCEPTANCE_OUTDIR"
acceptance_summary_status=$?

echo "[GeneFam] Refreshing delivery bundle with local acceptance summary"
"$PYTHON_BIN" bin/genefam/run_delivery_bundle.py \
  --release-checks "$RELEASE_OUTDIR/release_checks.tsv" \
  --objective-audit results/objective_audit/objective_audit.tsv \
  --readiness results/readiness/command_readiness.tsv \
  --quickstart "$QUICKSTART_OUTDIR/quickstart_summary.tsv" \
  --outdir "$DELIVERY_OUTDIR"
final_delivery_status=$?

echo "[GeneFam] Primary handoff files:"
echo "- results/handoff/handoff_report.md"
echo "- results/handoff/handoff_summary.tsv"
echo "- ${DELIVERY_OUTDIR}/delivery_manifest.tsv"
echo "- ${DELIVERY_OUTDIR}/delivery_bundle.md"
echo "- ${RELEASE_OUTDIR}/release_checks.md"
echo "- ${PUBLICATION_OUTDIR}/publication_report_audit.md"
echo "- ${PUBLICATION_OUTDIR}/wgd_publication_report_audit.md"
echo "- ${REPORT_INDEX_OUTDIR}/standard_report_index_audit.md"
echo "- ${REPORT_INDEX_OUTDIR}/wgd_report_index_audit.md"
echo "- ${QUICKSTART_OUTDIR}/quickstart_summary.md"
echo "- ${ACCEPTANCE_OUTDIR}/local_acceptance_summary.tsv"
echo "- ${ACCEPTANCE_OUTDIR}/local_acceptance_summary.md"

if [ "$release_status" -ne 0 ]; then
  echo "[GeneFam] Release gate exited with status ${release_status}."
  echo "[GeneFam] Inspect results/handoff/handoff_report.md for blockers."
fi

if [ "$publication_status" -ne 0 ]; then
  echo "[GeneFam] Publication report audit exited with status ${publication_status}."
fi
if [ "$standard_report_index_status" -ne 0 ]; then
  echo "[GeneFam] Standard report index audit exited with status ${standard_report_index_status}."
fi
if [ "$wgd_publication_status" -ne 0 ]; then
  echo "[GeneFam] WGD publication report audit exited with status ${wgd_publication_status}."
fi
if [ "$wgd_report_index_status" -ne 0 ]; then
  echo "[GeneFam] WGD report index audit exited with status ${wgd_report_index_status}."
fi

if [ "$quickstart_status" -ne 0 ]; then
  echo "[GeneFam] Quickstart handoff exited with status ${quickstart_status}."
fi

if [ "$delivery_status" -ne 0 ]; then
  echo "[GeneFam] Delivery bundle exited with status ${delivery_status}."
fi

if [ "$acceptance_summary_status" -ne 0 ]; then
  echo "[GeneFam] Local acceptance summary exited with status ${acceptance_summary_status}."
fi

if [ "$final_delivery_status" -ne 0 ]; then
  echo "[GeneFam] Final delivery bundle refresh exited with status ${final_delivery_status}."
fi

if [ "$release_status" -ne 0 ]; then
  exit "$release_status"
fi

if [ "$publication_status" -ne 0 ]; then
  exit "$publication_status"
fi
if [ "$standard_report_index_status" -ne 0 ]; then
  exit "$standard_report_index_status"
fi
if [ "$wgd_publication_status" -ne 0 ]; then
  exit "$wgd_publication_status"
fi
if [ "$wgd_report_index_status" -ne 0 ]; then
  exit "$wgd_report_index_status"
fi

if [ "$quickstart_status" -ne 0 ]; then
  exit "$quickstart_status"
fi

if [ "$delivery_status" -ne 0 ]; then
  exit "$delivery_status"
fi

if [ "$final_delivery_status" -ne 0 ]; then
  exit "$final_delivery_status"
fi

exit "$acceptance_summary_status"
