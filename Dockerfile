FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV TMBD_API_Key=9f54c65f9ac167982908b5b27bb2c622

EXPOSE 8000

COPY start_point.sh /start_point.sh

RUN chmod +x /start_point.sh

CMD ["/start_point.sh"]
