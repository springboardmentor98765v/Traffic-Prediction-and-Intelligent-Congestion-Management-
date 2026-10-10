# TrafficVision AI - Production Frontend Container
# Milestone 4 Production Release (Intern 4 -> Intern 5 CI/CD Hand-off)
FROM nginx:1.25-alpine

LABEL maintainer="TrafficVision AI Team <intern4@trafficvision.ai>"
LABEL description="Production Nginx container for TrafficVision AI Frontend"

# Set working directory
WORKDIR /usr/share/nginx/html

# Remove default nginx static assets
RUN rm -rf ./*

# Copy frontend static web assets
COPY . /usr/share/nginx/html

# Copy custom production Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/Login.html || exit 1

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
