FROM python:3.9-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    unzip \
    --no-install-recommends && rm -rf /var/lib/apt/lists/*

# Install Microsoft Edge stable
RUN wget -qO- https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    echo "deb [arch=amd64] https://packages.microsoft.com/repos/edge stable main" > /etc/apt/sources.list.d/microsoft-edge.list && \
    apt-get update && apt-get install -y microsoft-edge-stable && rm -rf /var/lib/apt/lists/*

# Download and install msedgedriver (adjust version as needed)
RUN wget -q https://msedgedriver.azureedge.net/114.0.1823.67/edgedriver_linux64.zip && \
    unzip edgedriver_linux64.zip && mv msedgedriver /usr/bin/ && chmod +x /usr/bin/msedgedriver && rm edgedriver_linux64.zip

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Expose port 10000 (or your chosen port)
EXPOSE 10000

# Run the Flask app
CMD ["python", "main.py"]
