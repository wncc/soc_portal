# # Build stage
# FROM node:20-alpine as build

# # Set working directory
# WORKDIR /app

# # Install pnpm
# RUN npm install -g pnpm

# # Copy package files
# COPY package.json pnpm-lock.yaml ./

# # Install dependencies
# RUN pnpm install

# # Copy source code
# COPY . .

# # Build the application
# RUN pnpm run build

# # Production stage
# FROM nginx:alpine

# # Copy built files from build stage
# COPY --from=build /app/build /usr/share/nginx/html

# # Copy nginx configuration
# COPY nginx.conf /etc/nginx/conf.d/default.conf

# # Expose port 80
# EXPOSE 80

# # Start nginx
# CMD ["nginx", "-g", "daemon off;"] 

# Build stage
FROM node:20-alpine as build

# Set working directory
WORKDIR /app

# Install pnpm
RUN npm install -g pnpm

# Copy package files
COPY package.json pnpm-lock.yaml ./

# Install dependencies
RUN pnpm install

# Copy source code
COPY . .

# Accept build arguments from Coolify
ARG REACT_APP_BACKEND_URL
ARG REACT_APP_API_URL
ARG REACT_APP_FRONTEND_URL

# Set as environment variables for the build
ENV REACT_APP_BACKEND_URL=$REACT_APP_BACKEND_URL
ENV REACT_APP_API_URL=$REACT_APP_API_URL
ENV REACT_APP_FRONTEND_URL=$REACT_APP_FRONTEND_URL

# Build the application
RUN pnpm run build

# Production stage
FROM nginx:alpine

# Copy built files from build stage
COPY --from=build /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
