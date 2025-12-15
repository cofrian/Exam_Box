#!/bin/bash
# Submit exam script
# Compresses the work directory and sends it to the exam manager

WORK_DIR="/home/student/work"
STUDENT_ID="${STUDENT_ID:-unknown}"
EXAM_MANAGER_URL="${EXAM_MANAGER_URL:-http://exam-manager:8000}"

echo "Preparing submission..."

# Create pip freeze
pip freeze > "${WORK_DIR}/pip_freeze.txt"

# Create timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
ZIP_FILE="/tmp/submission_${STUDENT_ID}_${TIMESTAMP}.zip"

# Create zip archive
cd "${WORK_DIR}"
zip -r "${ZIP_FILE}" . -x "*.pyc" -x "__pycache__/*" -x ".ipynb_checkpoints/*"

echo "Submission created: ${ZIP_FILE}"
echo "Size: $(du -h ${ZIP_FILE} | cut -f1)"

# Upload to exam manager (if running)
if curl -s "${EXAM_MANAGER_URL}/health" > /dev/null 2>&1; then
    echo "Uploading to exam manager..."
    # The actual upload is handled by the web interface
    echo "Upload handled by web interface"
else
    echo "Exam manager not reachable, submission saved locally"
fi

echo "Submission complete!"
