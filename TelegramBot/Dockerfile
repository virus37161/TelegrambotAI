FROM python:3.12
WORKDIR /app
COPY requirement.txt requirement.txt
RUN pip3 install --upgrade setuptools
RUN pip3 install -r requirement.txt
RUN chmod 755 .
COPY . .