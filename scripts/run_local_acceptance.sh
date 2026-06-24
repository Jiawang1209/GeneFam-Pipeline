#!/usr/bin/env bash

set -u

PYTHON_BIN=${PYTHON_BIN:-python}
CONDA_ENV=${CONDA_ENV:-GeneFamilyFlow}
RELEASE_OUTDIR=${RELEASE_OUTDIR:-results/release_checks}
QUICKSTART_OUTDIR=${QUICKSTART_OUTDIR:-results/quickstart}
DELIVERY_OUTDIR=${DELIVERY_OUTDIR:-results/delivery_bundle}

echo "[GeneFam] Running release gate into ${RELEASE_OUTDIR}"
"$PYTHON_BIN" bin/genefam/run_release_checks.py --outdir "$RELEASE_OUTDIR"
release_status=$?

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

echo "[GeneFam] Primary handoff files:"
echo "- results/handoff/handoff_report.md"
echo "- results/handoff/handoff_summary.tsv"
echo "- ${DELIVERY_OUTDIR}/delivery_manifest.tsv"
echo "- ${DELIVERY_OUTDIR}/delivery_bundle.md"
echo "- ${RELEASE_OUTDIR}/release_checks.md"
echo "- ${QUICKSTART_OUTDIR}/quickstart_summary.md"

if [ "$release_status" -ne 0 ]; then
  echo "[GeneFam] Release gate exited with status ${release_status}."
  echo "[GeneFam] Inspect results/handoff/handoff_report.md for blockers."
fi

if [ "$quickstart_status" -ne 0 ]; then
  echo "[GeneFam] Quickstart handoff exited with status ${quickstart_status}."
fi

if [ "$delivery_status" -ne 0 ]; then
  echo "[GeneFam] Delivery bundle exited with status ${delivery_status}."
fi

if [ "$release_status" -ne 0 ]; then
  exit "$release_status"
fi

if [ "$quickstart_status" -ne 0 ]; then
  exit "$quickstart_status"
fi

exit "$delivery_status"
