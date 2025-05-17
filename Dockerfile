FROM python:3.9-slim

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY pyproject.toml .
COPY README.md .

# Install dependencies
RUN pip install -e .

# Copy the rest of the application
COPY . .

# Expose the port Streamlit runs on
EXPOSE 8501

# Set environment variables
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Command to run the application
CMD ["streamlit", "run", "app.py"]
