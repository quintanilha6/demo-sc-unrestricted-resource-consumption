FROM python:3.12
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
COPY api/internal /app
EXPOSE 8000
CMD ["gunicorn", "-b", "0.0.0.0:8000", "internal_address_validator:app"]
