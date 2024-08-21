# How usage flask-boilerpate

## Clone Repository

```
git clone git@github.com:jrdiniz/flask-boilerplate.git . 
```

## Create Virtual Environment

I have test this project with 3.10, with you test with another version, please open a pull request to update the documentation.

```
python3.10 -m venv env
```

## Install Dependencies 

```
source env/bin/active
pip install -r requirements.txt
```

## Environment Configuration

The project use python-dotenv library, so you need create an .env file on root directory:

 - Development Environment 

```
FLASK_APP=app
FLASK_DEBUG=True
FLASK_CONFIG_FILE=config.DevelopmentConfig
SECRET_KEY=<your-secret-key>

```

 - Production Environment

```
FLASK_APP=app
FLASK_DEBUG=False
FLASK_CONFIG_FILE=config.ProductionConfig
SECRET_KEY=<your-secret-key>

```

# Library

 - Bootstrap5
 - Bootstrap Icons
 - HTMX

## Deploy with Docker

Built app image

```
docker built -t flask-boilerplate .
```

To run the container

```
docker run -p -d <host-port>:5000 --name <project-name> flask-boilerplate
```

To deploy the container

```
docker exec -it <container-id> bash
```

## Deploy using Ansible

