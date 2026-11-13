
# 1. Start with a lightweight Python image
FROM python:3.13-slim

# 2. Prevent Python from creating .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# 3. Send Python logs directly to the container output
ENV PYTHONUNBUFFERED=1

# 4. Set the working directory inside the container
WORKDIR /app

# 5. Install Python dependencies first
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the application source code
COPY . .

# 7. Create an unprivileged application user
RUN addgroup --system app && adduser --system --ingroup app app \
    && chown -R app:app /app

# 8. Run the application as a non-root user
USER app

# 9. Document the application port
EXPOSE 8000

# 10. Start Django using Gunicorn
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
