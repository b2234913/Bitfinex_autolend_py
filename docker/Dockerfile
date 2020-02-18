FROM python:3.8.1

COPY ./bitfinex-api-py /bitfinex-api-py
WORKDIR /bitfinex-api-py
RUN pip3 install -r requirements.txt
RUN python3 setup.py install
COPY ./auto_lend.py /app/auto_lend.py
# COPY ./config.json /app/config.json
# WORKDIR /app
# ENTRYPOINT ["python3", "auto_lend.py"]