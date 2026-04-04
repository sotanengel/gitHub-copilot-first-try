#!/bin/bash
# Export Marp slides to PDF, skipping if text content is unchanged.
# This avoids infinite loops in pre-commit caused by non-deterministic
# PDF timestamps produced by marp on every run.
set -euo pipefail

SLIDES_MD="slides/slides.md"
SLIDES_PDF="slides/slides.pdf"
TMP_PDF=$(mktemp /tmp/marp_XXXXXX.pdf)
TMP_NEW_TXT=$(mktemp /tmp/marp_new_XXXXXX.txt)
TMP_OLD_TXT=$(mktemp /tmp/marp_old_XXXXXX.txt)

cleanup() {
    rm -f "${TMP_PDF}" "${TMP_NEW_TXT}" "${TMP_OLD_TXT}"
}
trap cleanup EXIT

marp "${SLIDES_MD}" --pdf -o "${TMP_PDF}"

if [ -f "${SLIDES_PDF}" ]; then
    pdftotext "${TMP_PDF}" "${TMP_NEW_TXT}"
    pdftotext "${SLIDES_PDF}" "${TMP_OLD_TXT}"
    if diff -q "${TMP_NEW_TXT}" "${TMP_OLD_TXT}" > /dev/null 2>&1; then
        echo "PDF is already up to date"
        exit 0
    fi
fi

cp "${TMP_PDF}" "${SLIDES_PDF}"
echo "PDF updated: ${SLIDES_PDF}"
