# Deployment Guide

This guide provides instructions for deploying the SOC Portal (backend and frontend) to production servers.

## Prerequisites

- Docker and Docker Compose installed on the server
- Domain names configured:
  - Frontend: soc.tech-iitb.org
  - Backend: socb.tech-iitb.org

## Environment Files

### Backend (.env)

Create a `.env` file in the `socbackend` directory with the following content:

```
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
DJANGO_SECRET_KEY=your_secure_secret_key
DJANGO_DEBUG=False
```

### Frontend (.env)

Create a `.env` file in the `socfrontend` directory with the following content:

```
REACT_APP_BACKEND_URL=https://socb.tech-iitb.org/api
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
DOMAIN_NAME=https://soc.tech-iitb.org/
```

## Deployment Steps

1. Clone the repository on your server:

   ```
   git clone https://github.com/DeepakSilaych/soc_portal.git
   cd soc_portal
   ```

2. Set up environment files as described above.

3. Deploy using Docker Compose:

   ```
   docker-compose up -d --build
   ```

4. Set up Nginx reverse proxy on the server:

   Create a configuration file for each domain:

   ### For soc.tech-iitb.org:

   ```
   server {
       listen 80;
       server_name soc.tech-iitb.org;

       # Redirect HTTP to HTTPS
       location / {
           return 301 https://$host$request_uri;
       }
   }

   server {
       listen 443 ssl;
       server_name soc.tech-iitb.org;

       ssl_certificate /path/to/cert.pem;
       ssl_certificate_key /path/to/key.pem;

       location / {
           proxy_pass http://localhost:80;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

   ### For socb.tech-iitb.org:

   ```
   server {
       listen 80;
       server_name socb.tech-iitb.org;

       # Redirect HTTP to HTTPS
       location / {
           return 301 https://$host$request_uri;
       }
   }

   server {
       listen 443 ssl;
       server_name socb.tech-iitb.org;

       ssl_certificate /path/to/cert.pem;
       ssl_certificate_key /path/to/key.pem;

       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }

       # Serve static files directly
       location /static/ {
           alias /path/to/static/;
       }

       location /media/ {
           alias /path/to/media/;
       }
   }
   ```

5. Obtain SSL certificates using Let's Encrypt:

   ```
   sudo certbot --nginx -d soc.tech-iitb.org -d socb.tech-iitb.org
   ```

6. Restart Nginx to apply the changes:
   ```
   sudo systemctl restart nginx
   ```

## Troubleshooting

- Check container logs if there are issues:

  ```
  docker logs soc-backend
  docker logs soc-frontend
  ```

- If static files aren't being served correctly, ensure the volumes are properly mounted and the Nginx configuration is pointing to the correct locations.

- For database issues, you can connect to the backend container:
  ```
  docker exec -it soc-backend bash
  ```
