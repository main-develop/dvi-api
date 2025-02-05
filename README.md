# DVI api

DVI microservice responsible for processing and maintaining user data.

## Installation

The microservice source code should be located in a separate subdirectory. If the parent directory does not exist yet, it must be created. You can replace `parent-dir` with any directory name of your choice.

### Windows

```
> mkdir parent-dir\dvi-api
> cd parent-dir
> git clone https://github.com/main-develop/dvi-api.git ./dvi-api
```

### macOS & Linux

```
> mkdir -p parent-dir/dvi-api
> cd parent-dir
> git clone https://github.com/main-develop/dvi-api.git ./dvi-api
```

## Setup environment

A sample `.env.sample` environment variable file is located in the root directory of the cloned project. It contains the following variables:

```conf
SECRET_KEY="your secret key"

SQLALCHEMY_DATABASE_URI="postgresql://postgres:your-password@db:5432/dvi_backend"
```

where:

- `SECRET_KEY` - replace `"your secret key"` with a randomly generated string of at least 28 characters;
- `SQLALCHEMY_DATABASE_URI` - database connection path. Any password can be specified instead of `your-password`.

For the project to work properly, you must change the name of this file to `.env`.

## Setup additional components

For a fully functional DVI system, the final project structure should look like this:

```yml
├─ db/                  # PostgreSQL database directory
│  └─ .db.env           # PostgreSQL environment variable file
├─ dvi-api/             # User data processing and maintaining microservice directory
├─ dvi-frontend/        # Web interface source code directory
├─ dvi-logging/         # Logs collecting, aggregating and sending microservice directory
├─ nginx/               # NGINX service directory
│  └─ nginx.conf        # NGINX configuration file
├─ redis/               # Redis service directory
├─ .env                 # Elasticsearch and Kibana environment variable file
├─ docker-compose.yml   # Docker Compose configuration file
└─ logstash.conf        # Logstash configuration file
```

This section can be skipped if all necessary components have been created.

### Setup PostgreSQL environment variable file

For the database to work properly, the `.db.env` file must contain the following variables:

```conf
POSTGRES_USER="postgres"
POSTGRES_PASSWORD="your password"
POSTGRES_DB="dvi_backend"
```

where:

- `POSTGRES_PASSWORD` - any password can be specified instead of `"your password"`.

### DVI frontend installation

For Windows:

```
> mkdir parent-dir\dvi-frontend
> cd parent-dir
> git clone https://github.com/main-develop/dvi-frontend.git ./dvi-fronted
```

For macOS & Linux:

```
> mkdir -p parent-dir/dvi-frontend
> cd parent-dir
> git clone https://github.com/main-develop/dvi-frontend.git ./dvi-frontend
```

### DVI logging installation

For Windows:

```
> mkdir parent-dir\dvi-logging
> cd parent-dir
> git clone https://github.com/main-develop/dvi-logging.git ./dvi-logging
```

For macOS & Linux:

```
> mkdir -p parent-dir/dvi-logging
> cd parent-dir
> git clone https://github.com/main-develop/dvi-logging.git ./dvi-logging
```

### Setup NGINX configuration file

For basic load balancing and request distribution through NGINX, you must create a configuration file with the following contents in the `nginx` directory:

```conf
events {
    worker_connections 1024;
}

http {
    upstream api_servers {
        server api:5000;
    }

    upstream logging_servers {
        server logging:5001;
    }

    upstream frontend_servers {
        server frontend:3000;
    }

    server {
        listen 80;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        location /dvi-api/ {
            proxy_pass http://api_servers;
        }

        location /dvi-logging/ {
            proxy_pass http://logging_servers;
        }

        location / {
            proxy_pass http://frontend_servers;
        }
    }
}
```

### Setup Elasticsearch and Kibana environment variable file

To properly handle logs using Elasticsearch and Kibana services, a `.env` file with the following contents must be created in the root of the parent directory:

```conf
ELASTIC_PASSWORD="your password"
KIBANA_PASSWORD="your password"
SAVED_OBJECTS_ENCRYPTION_KEY="your encryption key"
STACK_VERSION=8.17.1
LICENSE=basic
ES_PORT=127.0.0.1:9200
KIBANA_PORT=5601
```

where:

- `ELASTIC_PASSWORD`, `KIBANA_PASSWORD` - any password can be specified instead of `"your password"`;
- `SAVED_OBJECTS_ENCRYPTION_KEY` - replace `"your encryption key"` with a randomly generated string of at least 28 characters.

### Setup Logstash configuration file

To collect and send logs using Logstash to the Elasticsearch log store, you must create a `logstash.conf` file with the following contents in the root of the parent directory:

```conf
input {
    udp {
        port => 5002
        codec => json {
            target => "[document]"
        }
    }
}

filter {
  # Add processing logic here if needed
}

output {
    elasticsearch {
        hosts => ["http://elasticsearch:9200/"]
        index => "dvi-logging"
    }
}
```

### Setup Docker Compose configuration file

To run all necessary services and try out the DVI system, you must create a `docker-compose.yml` file with the following contents in the root of the directory:

```yml
services:
  # PostgreSQL service
  db:
    restart: always
    image: postgres:latest
    ports:
      - "5432:5432"
    env_file:
      - ./db/.db.env
    volumes:
      - ./db/pData:/var/lib/postgresql/data
    healthcheck:
      test:
        ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB} -t 1"]
      interval: 10s
      timeout: 10s
      retries: 10
      start_period: 10s

  # Redis service
  redis:
    restart: always
    image: redis:latest
    ports:
      - "6379:6379"
    volumes:
      - ./redis:/data

  # API service
  api:
    restart: always
    build:
      context: ./dvi-api
      dockerfile: Dockerfile
    volumes:
      - ./dvi-api/src:/app/src
    ports:
      - "5000:5000"
    env_file:
      - ./dvi-api/.env
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    command: >
      sh -c "flask db upgrade --directory src/migrations || echo 'Migration failed' && gunicorn -w 4 -b 0.0.0.0:5000 --chdir src app:app"

  # Logging service
  logging:
    restart: always
    build:
      context: ./dvi-logging
      dockerfile: Dockerfile
    volumes:
      - ./dvi-logging/src:/app/src
    ports:
      - "5001:5001"
    depends_on:
      - api
    command: >
      sh -c "gunicorn -w 4 -b 0.0.0.0:5001 --chdir src app:app"

  # Frontend service
  frontend:
    restart: always
    build:
      context: ./dvi-frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    depends_on:
      - api

  # NGINX service
  nginx:
    restart: always
    image: nginx:latest
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - api
      - logging
      - frontend

  # Elasticsearch service
  elasticsearch:
    restart: always
    image: docker.elastic.co/elasticsearch/elasticsearch:${STACK_VERSION}
    ports:
      - "${ES_PORT}:9200"
    environment:
      - discovery.type=single-node
      - ES_JAVA_OPTS=-Xms512m -Xmx512m
      - ELASTIC_PASSWORD=${ELASTIC_PASSWORD}
      - xpack.license.self_generated.type=${LICENSE}
      - xpack.security.enabled=false # Only for development
      - xpack.security.http.ssl.enabled=false # Only for development
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
    healthcheck:
      test:
        ["CMD-SHELL", "curl -s http://localhost:9200 | grep -q 'cluster_name'"]
      interval: 10s
      timeout: 10s
      retries: 10
      start_period: 10s

  # Logstash service
  logstash:
    restart: always
    image: docker.elastic.co/logstash/logstash:${STACK_VERSION}
    ports:
      - "5002:5002"
    environment:
      - LS_JAVA_OPTS=-Xms512m -Xmx512m
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf:ro
    depends_on:
      elasticsearch:
        condition: service_healthy

  # Kibana service
  kibana:
    restart: always
    image: docker.elastic.co/kibana/kibana:${STACK_VERSION}
    ports:
      - "${KIBANA_PORT}:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
      - ELASTICSEARCH_PASSWORD=${KIBANA_PASSWORD}
      - XPACK_ENCRYPTEDSAVEDOBJECTS_ENCRYPTIONKEY=${SAVED_OBJECTS_ENCRYPTION_KEY}
    depends_on:
      elasticsearch:
        condition: service_healthy

volumes:
  elasticsearch_data:
    driver: local
```

## Run Docker Compose

To run the DVI system, execute the specified command in the root of the parent directory:

```
> docker-compose up --build
```

The web interface will then be available at http://localhost:3000.
