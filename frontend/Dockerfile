# Use Node.js 20 LTS
FROM node:20-alpine

# Set working directory inside container
WORKDIR /app

# Copy package files first (for better caching)
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Expose port 3000 for Vite dev server
EXPOSE 3000

# Run Vite dev server with hot reload
# --host allows external connections (needed for Docker)
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]
