FROM python:3.11-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

# Build with the model:  docker build --build-arg WITH_MODEL=1 -t clinical-nlp .
ARG WITH_MODEL=0
COPY requirements.txt requirements-model.txt ./
RUN if [ "$WITH_MODEL" = "1" ]; then pip install --no-cache-dir -r requirements-model.txt; \
    else pip install --no-cache-dir -r requirements.txt; fi

COPY clinical_nlp ./clinical_nlp
COPY data ./data
COPY app.py evaluate.py ./

EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
