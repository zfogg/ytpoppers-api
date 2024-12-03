FROM public.ecr.aws/docker/library/python:3.8.12-slim-buster
COPY --from=public.ecr.aws/awsguru/aws-lambda-adapter:0.8.4 /lambda-adapter /opt/extensions/lambda-adapter
WORKDIR /var/task
COPY main.py requirements.txt .env api/ ./
COPY api/ ./api
RUN python3.8 -m pip install -r requirements.txt
CMD ["python", "main.py"]