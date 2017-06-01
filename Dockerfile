FROM        ubuntu:16.04
FROM        python:3.5
ADD         requirements.txt /app/
WORKDIR     /app
RUN         apt-get update & apt-get install gcc -y
RUN         pip install -r /app/requirements.txt
ADD         . /app
EXPOSE      5000
CMD         ["./manage.py", "db init"]
CMD         ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "wsgi:app"]
