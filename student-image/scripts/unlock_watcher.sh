#!/bin/bash
# Watches for new questions to be unlocked by the professor
# Copies questions from template to work directory

WORK_DIR="/home/student/work"
TEMPLATE_DIR="/home/student/exam_template"
NUM_QUESTIONS="${NUM_QUESTIONS:-3}"
EXAM_MANAGER_URL="${EXAM_MANAGER_URL:-http://exam-manager:8000}"
STUDENT_ID="${STUDENT_ID:-unknown}"

echo "Starting unlock watcher..."
echo "Monitoring for questions 1-${NUM_QUESTIONS}"

while true; do
    # Check which questions should be unlocked via API
    # For now, we'll check if files appear in the work directory
    # The exam-manager copies files when professor unlocks
    
    for i in $(seq 1 ${NUM_QUESTIONS}); do
        TEMPLATE_Q="${TEMPLATE_DIR}/Q${i}"
        WORK_Q="${WORK_DIR}/Q${i}"
        
        # If template exists but work doesn't, check if we should copy
        if [ -d "${TEMPLATE_Q}" ] && [ ! -d "${WORK_Q}" ]; then
            # Check for unlock signal file
            SIGNAL_FILE="${WORK_DIR}/.unlock_Q${i}"
            if [ -f "${SIGNAL_FILE}" ]; then
                echo "Unlocking Q${i}..."
                cp -r "${TEMPLATE_Q}" "${WORK_Q}"
                rm -f "${SIGNAL_FILE}"
                echo "Q${i} unlocked successfully!"
            fi
        fi
    done
    
    sleep 5
done
