FROM python:3.9-alpine
COPY saffrun .
WORKDIR saffrun
EXPOSE 8000 8000
CMD ["manage.py", "runserver"]