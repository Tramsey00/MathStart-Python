# Development/test infrastructure only; not a production server image.
FROM python:3.12-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.lock ./
RUN python -m pip install --no-cache-dir --no-deps -r requirements.lock && python -m pip check
COPY . .
RUN useradd --uid 10001 --create-home mathstart && mkdir -p /runtime && chown mathstart:mathstart /runtime
USER mathstart
ENV DJANGO_RUNTIME_ROOT=/runtime
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000", "--noreload"]
