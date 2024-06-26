# Use the NVIDIA base image with CUDA and PyTorch
FROM nvidia/cuda:11.8.0-devel-ubuntu22.04

# sys
RUN apt-get update --yes --quiet && DEBIAN_FRONTEND=noninteractive apt-get install --yes --quiet --no-install-recommends \
    software-properties-common \
    build-essential apt-utils \
    wget curl vim git ca-certificates kmod \
    nvidia-driver-525 \
    && rm -rf /var/lib/apt/lists/*

# PYTHON 3.10
RUN add-apt-repository --yes ppa:deadsnakes/ppa && apt-get update --yes --quiet
RUN DEBIAN_FRONTEND=noninteractive apt-get install --yes --quiet --no-install-recommends \
    python3.10 \
    python3.10-dev \
    python3.10-distutils \
    python3.10-lib2to3 \
    python3.10-gdbm \
    python3.10-tk \
    pip

RUN pip install --upgrade pip

# Set the working directory in the container
WORKDIR /

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN python3 -m pip install --no-cache-dir -r requirements.txt
RUN python3 --version

# Copy the rest of the application code to the working directory
COPY . .

RUN chmod +x run.sh
CMD ["./run.sh"]

