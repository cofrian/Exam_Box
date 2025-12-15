# ExamBox Student Image
# JupyterLab environment for exam participants

FROM python:3.11-slim-bookworm

# Build arguments
ARG NB_USER=student
ARG NB_UID=1000
ARG NB_GID=100

# Environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOME=/home/${NB_USER} \
    SHELL=/bin/bash

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    zip \
    unzip \
    sudo \
    locales \
    fonts-liberation \
    && locale-gen en_US.UTF-8 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -s /bin/bash -N -u ${NB_UID} ${NB_USER} && \
    echo "${NB_USER} ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Create directories
RUN mkdir -p /home/${NB_USER}/work \
    /home/${NB_USER}/materials \
    /home/${NB_USER}/exam_template \
    /home/${NB_USER}/.jupyter \
    /scripts

# Install Python packages for JupyterLab
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Habilitar extensiones de JupyterLab (PDF viewer)
RUN jupyter labextension list

# Copy startup and utility scripts
COPY scripts/ /scripts/
RUN chmod +x /scripts/*.sh

# Copy Jupyter configuration
COPY jupyter_notebook_config.py /home/${NB_USER}/.jupyter/

# Create materials and pdf folder
RUN mkdir -p /home/${NB_USER}/materials/pdfs

# Set ownership
RUN chown -R ${NB_USER}:${NB_GID} /home/${NB_USER} /scripts

# Switch to non-root user
USER ${NB_USER}
WORKDIR /home/${NB_USER}/work

# Expose Jupyter port
EXPOSE 8888

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8888/api || exit 1

# Entrypoint
ENTRYPOINT ["/scripts/entrypoint.sh"]
