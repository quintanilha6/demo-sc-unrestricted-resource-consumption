FROM python:3.12
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
COPY api/external /app
EXPOSE 8001
CMD ["gunicorn", "-b", "0.0.0.0:8001", "external_address_provider:app"]
