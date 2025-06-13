FROM continuumio/miniconda3:latest

# Install TeX Live and other system packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        texlive-latex-extra \
        curl \
        unzip \
        make \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy and create conda environment
COPY environment.yml /tmp/environment.yml
RUN conda env create -f /tmp/environment.yml && \
    conda clean -afy

# Set the environment path
ENV PATH="/opt/conda/envs/$(head -1 /tmp/environment.yml | cut -d' ' -f2)/bin:$PATH"

# Activate env by default
SHELL ["conda", "run", "-n", "$(head -1 /tmp/environment.yml | cut -d' ' -f2)", "/bin/bash", "-c"]
