FROM python:3.9.5

WORKDIR /tranche-monitor

# Update pip
RUN pip install -U \
    pip

# Install dependencys
RUN pip install Flask
RUN pip install web3

# Expose flask's default port
EXPOSE 5000

# Copy and start the app
COPY . .
ENTRYPOINT ["flask", "run", "--host=0.0.0.0"]