
1.be sure about the gunicorn command to trigger the flask app
====
2.create dir that contains the your own project:RUN mkdir /app/flask_app
====
3.add the whole prject files to the dir just created :ADD flask_app/ /app/flask_app
====
4.change the expose port of Docker and the listen port of nginx
====
