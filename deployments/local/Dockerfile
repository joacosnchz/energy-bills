FROM python:3.10-slim-buster

COPY deployments/local/requirements.txt .

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

WORKDIR /app

COPY src/ /app

ENTRYPOINT ["python"]

CMD ["-m", "energy_bills"]
