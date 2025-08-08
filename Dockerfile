# El Programming Language Docker Image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

# Copy source code
COPY compiler/ ./compiler/
COPY utils/ ./utils/
COPY system/ ./system/
COPY examples/ ./examples/
COPY el_standalone.py .
COPY el_cli.py .

# Install Python dependencies
RUN pip install --no-cache-dir pyinstaller pillow

# Build the executable
RUN pyinstaller --onefile --name el --console --add-data "compiler:compiler" --add-data "utils:utils" --add-data "system:system" --add-data "examples:examples" --hidden-import compiler --hidden-import utils --hidden-import system el_standalone.py

# Make executable available in PATH
RUN cp dist/el /usr/local/bin/el

# Create non-root user
RUN useradd -m -s /bin/bash eluser
USER eluser
WORKDIR /home/eluser

# Set entrypoint
ENTRYPOINT ["el"]
CMD ["--help"]

# Metadata
LABEL org.opencontainers.image.title="El Programming Language"
LABEL org.opencontainers.image.description="A modern and easy programming language"
LABEL org.opencontainers.image.source="https://github.com/Daftyon/Easier-language"
LABEL org.opencontainers.image.version="1.0.5"
