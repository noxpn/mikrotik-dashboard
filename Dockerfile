FROM python:slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 5080/tcp
VOLUME /app/mkdashboard/db
ENTRYPOINT ["python"]
CMD ["nxapp.py"]
