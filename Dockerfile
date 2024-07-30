# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Install system dependencies, GDAL dependencies, and NVIDIA container toolkit
RUN apt-get update && apt-get install -y --no-install-recommends \
    vim git curl build-essential libzmq3-dev libgfortran5 \
    gcc g++ gfortran libxml2-dev libssl-dev libcurl4-openssl-dev \
    gnupg lsb-release sudo wget dos2unix cmake \
    libproj-dev libgeos-dev libsqlite3-dev libpng-dev \
    libjpeg-dev libtiff-dev libgif-dev libwebp-dev libopenjp2-7-dev \
    libnetcdf-dev libpoppler-dev libspatialite-dev libhdf4-alt-dev \
    libhdf5-dev libfreexl-dev libxerces-c-dev libexpat-dev \
    libpcre3-dev libcairo2-dev libxml2-dev \
    && apt-get update \
    && rm -rf /var/lib/apt/lists/*

# Ensure compatible versions of libnetcdf and libcurl are installed
RUN apt-get install -y --reinstall libnetcdf19 libcurl4

# Install GDAL from source with detailed logging
RUN echo "Downloading GDAL 3.9.1" && \
    curl -L https://github.com/OSGeo/gdal/releases/download/v3.9.1/gdal-3.9.1.tar.gz -o gdal-3.9.1.tar.gz && \
    echo "Extracting GDAL 3.9.1" && \
    tar -xvzf gdal-3.9.1.tar.gz && \
    cd gdal-3.9.1 && \
    echo "Creating build directory" && \
    mkdir build && cd build && \
    echo "Running cmake" && \
    cmake .. -DCMAKE_BUILD_TYPE=Release \
             -DCMAKE_INSTALL_PREFIX=/usr/local \
             -DGDAL_PYTHON_INSTALL_PREFIX=/usr/local/lib/python3.9/site-packages \
             -DCMAKE_CXX_FLAGS="-lcurl" -DCMAKE_C_FLAGS="-lcurl" && \
    echo "Running make" && \
    make -j$(nproc) && \
    echo "Running make install" && \
    make install && \
    echo "Running ldconfig" && \
    ldconfig && \
    cd ../.. && \
    echo "Cleaning up" && \
    rm -rf gdal-3.9.1 gdal-3.9.1.tar.gz

# Install GDAL Python bindings
RUN echo "Installing GDAL Python bindings" && \
    CPLUS_INCLUDE_PATH=/usr/include/gdal C_INCLUDE_PATH=/usr/include/gdal pip install gdal==3.9.1

# Install Python packages
RUN pip install --no-cache-dir \
    rasterio \
    geopandas \
    xarray \
    zarr \
    flask

# Verify GDAL installation
RUN gdalinfo --version

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Expose port 8000 for the Flask app
EXPOSE 8000

# Run the Flask app
CMD ["python", "main.py"]
