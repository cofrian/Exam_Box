#!/bin/bash
# ExamBox Student Container Entrypoint
# Prepares the workspace and starts JupyterLab

set -e

echo "============================================"
echo "  ExamBox Student Container Starting"
echo "============================================"
echo "Student ID: ${STUDENT_ID:-unknown}"
echo "Exam: ${EXAM_NAME:-unknown}"
echo "Questions: ${NUM_QUESTIONS:-3}"
echo "============================================"

# Create work directory structure
WORK_DIR="/home/student/work"
mkdir -p "${WORK_DIR}"

# Copy Q1 from exam template if not already present
TEMPLATE_DIR="/home/student/exam_template"
if [ -d "${TEMPLATE_DIR}/Q1" ] && [ ! -d "${WORK_DIR}/Q1" ]; then
    echo "Copying Q1 to workspace..."
    cp -r "${TEMPLATE_DIR}/Q1" "${WORK_DIR}/"
fi

# Create a welcome notebook if work dir is empty
if [ -z "$(ls -A ${WORK_DIR} 2>/dev/null)" ]; then
    echo "Creating welcome notebook..."
    cat > "${WORK_DIR}/Bienvenido.ipynb" << 'EOF'
{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Bienvenido al Examen\n",
    "\n",
    "Este es tu espacio de trabajo. Las preguntas se irán desbloqueando según avance el examen.\n",
    "\n",
    "**Instrucciones:**\n",
    "- Trabaja en las carpetas Q1, Q2, Q3... según se vayan desbloqueando\n",
    "- Guarda tu trabajo frecuentemente\n",
    "- Los materiales de consulta están en la carpeta `/home/student/materials`\n",
    "- Usa el botón **Entregar** cuando termines"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}
EOF
fi

# Start background process to check for unlocked questions
/scripts/unlock_watcher.sh &

# Start JupyterLab with iframe support
echo "Starting JupyterLab..."
exec jupyter lab \
    --ip=0.0.0.0 \
    --port=8888 \
    --no-browser \
    --ServerApp.token="${JUPYTER_TOKEN:-exambox123}" \
    --ServerApp.allow_origin='*' \
    --ServerApp.disable_check_xsrf=True \
    --ServerApp.allow_remote_access=True \
    --ServerApp.root_dir='/home/student/work' \
    --ServerApp.tornado_settings="{'headers': {'Content-Security-Policy': \"frame-ancestors 'self' http://localhost:* http://127.0.0.1:*\"}}"
