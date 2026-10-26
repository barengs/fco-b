FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
# Install CPU-only PyTorch to reduce image size, then install remaining requirements
RUN pip install --no-cache-dir torch==2.5.1 --extra-index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["gunicorn", "fco_project.wsgi:application", "--bind", "0.0.0.0:8000", "--timeout", "120", "--workers", "3"]
