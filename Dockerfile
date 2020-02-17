# choose python image
FROM python:2

# install needed pip packages
WORKDIR /usr/src/app
COPY server.py ./
COPY requirements.txt ./
RUN pip install -r requirements.txt

# run script from entry point
CMD [ "python", "./server.py" ]
