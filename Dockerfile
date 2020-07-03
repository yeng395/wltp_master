FROM minizinc/minizinc:latest

RUN apt-get update -y
RUN apt-get install -y software-properties-common
RUN add-apt-repository -y ppa:deadsnakes/ppa
RUN apt-get install -y python3.8
RUN apt-get install -y python3.8-venv
RUN apt-get install -y python3-pip python3.8-dev build-essential
RUN apt-get install -y sudo
RUN sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.6 1
RUN sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 2
RUN sudo update-alternatives --config python3
CMD ["2"]

RUN apt-get install -y bash

COPY Resources/couenne.msc /usr/local/share/minizinc/solvers/
COPY Resources/couenne-linux64 /couenne-linux64

RUN minizinc --solvers

WORKDIR /app
COPY . /app

RUN python3.8 -m venv venv
RUN pip3 install -r requirements.txt
RUN pip3 install minizinc

ENV FLASK_APP wltp.py

EXPOSE 8080
RUN chmod a+x boot.sh

ENTRYPOINT ["./boot.sh"]
