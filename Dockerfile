FROM minizinc/minizinc:latest-alpine

#ADD https://github.com/MiniZinc/MiniZincIDE/releases/download/2.1.7/MiniZincIDE-2.1.7-bundle-linux-x86_64.tgz /minizinc.tgz
#RUN tar -zxf /minizinc.tgz && \
#    mv /MiniZincIDE-2.1.7-bundle-linux-x86_64 /minizinc

#RUN apt-get update -y
#RUN apt-get install -y python3.7
#RUN apt-get install -y python3-pip python3.7-dev build-essential

RUN apk add --no-cache --virtual .build-deps g++ python3-dev libffi-dev openssl-dev && \
 apk add --no-cache --update python3 && \
  pip3 install --upgrade pip setuptools

RUN apk add bash
#RUN apt-get install -y bash

COPY Resources/couenne.msc /usr/local/share/minizinc/solvers/
COPY Resources/couenne-linux64 /couenne-linux64

RUN minizinc --solvers

WORKDIR /app
COPY . /app

RUN pip3 install -r requirements.txt
RUN pip3 install minizinc

ENV FLASK_APP wltp.py

EXPOSE 8080

ENTRYPOINT ["python3"]

RUN python3 --version

CMD ["wltp.py"]