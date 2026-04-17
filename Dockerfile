FROM python:3.12-slim

WORKDIR /app

# Copy dependency list
COPY requirements.txt .

# Install dependencies explicitly without cache to keep image small
RUN pip install --no-cache-dir -r requirements.txt

# Copy all source files
COPY . .

# Environment variables (override in compose or production)
ENV CONNECTION_STRING=sqlite:///data.db
ENV SECRET_KEY=changeme
ENV CLOUDFLARE_R2_API=none

EXPOSE 8000

# Automatically run alembic migrations on start or allow script 
CMD ["sh", "-c", "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000"]
