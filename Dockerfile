FROM python:3.9-alpine as build
RUN pip install --upgrade pip

RUN mkdir /app
COPY requirements.txt /app
COPY pyproject.toml /app
COPY AoCH/ /app/AoCH/
COPY static/ /app/static/
COPY templates/ /app/templates/

WORKDIR /app
RUN python -m pip install -r requirements.txt

EXPOSE 8080:8080
CMD ["waitress-serve", "--call", "AoCH:create_app"]
