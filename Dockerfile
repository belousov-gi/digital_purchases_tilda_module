FROM python:3.10.12
WORKDIR /main_app
COPY ./requirements.txt /main_app/requirements.txt
RUN pip install --upgrade -r /main_app/requirements.txt
COPY . /main_app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
