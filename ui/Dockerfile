FROM python:3.12
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
COPY ui /app
EXPOSE 8080
CMD ["python", "-m", "http.server", "8080"]
