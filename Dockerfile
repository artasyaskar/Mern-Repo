FROM node:20-alpine

WORKDIR /app

# Install deps first for better layer caching
COPY package*.json ./
RUN npm ci --no-audit --no-fund --prefer-offline || npm i --no-audit --no-fund --prefer-offline

# App source
COPY . .

# Ensure test runner is executable
RUN chmod +x /app/run_tests.sh

# Default entrypoint lets grader pass TASK_ID
ENTRYPOINT ["./run_tests.sh"]
