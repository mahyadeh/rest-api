FROM python:3.7
WORKDIR /app
RUN pip install PyMySQL
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY app app
COPY app.py config.py ./
ENV FLASK_APP app.py
ENV FLASK_DEBUG True
ENTRYPOINT ["python", "app.py"]
