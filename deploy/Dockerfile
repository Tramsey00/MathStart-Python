# Independent target images. API has no Node, Django or development server.
FROM node:24.21.0-bookworm-slim@sha256:d6aa754f16b3197301076f047b5def2f02ea1dbbc2ca920407d46d7ec7f87b20 AS node-toolchain
RUN npm install --global npm@11.19.0 --ignore-scripts --no-audit --no-fund

FROM python:3.12-slim-bookworm@sha256:34386ef0cb081344d7ec1c103ba398e6e9f64e9ab3a1509accc92a4e24a07258 AS python-runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*
COPY backend/requirements.lock /app/backend/requirements.lock
COPY backend/infrastructure/http/requirements.lock /app/backend/infrastructure/http/requirements.lock
RUN python -m pip install --no-deps -r backend/infrastructure/http/requirements.lock \
    && python -m pip check \
    && python -c "import importlib.util; assert importlib.util.find_spec('django') is None; assert importlib.util.find_spec('rest_framework') is None"
COPY backend /app/backend
COPY specs /app/specs
RUN useradd --uid 10001 --create-home mathstart \
    && mkdir -p /runtime && chown mathstart:mathstart /runtime

FROM python-runtime AS frontend-builder
COPY --from=node-toolchain /usr/local/bin/node /usr/local/bin/node
COPY --from=node-toolchain /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -s /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
    && ln -s /usr/local/lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx
COPY frontend /app/frontend
COPY static /app/static
RUN npm --prefix frontend ci --maxsockets=1 --no-audit --no-fund \
    && mkdir -p frontend/.cache frontend/build && chown -R mathstart:mathstart frontend
USER mathstart
ENTRYPOINT ["python", "-m", "frontend.build_public"]

FROM nginx:stable-bookworm@sha256:552e7481ca93ffccd046aa658dbbed22caefbc09c66fa7cd247cbb90b8a5c609 AS edge
COPY deploy/nginx.conf /etc/nginx/nginx.conf
COPY deploy/nginx.tls.conf /etc/nginx/nginx.tls.conf
COPY deploy/proxy.conf /etc/nginx/proxy.conf
USER 101:101
EXPOSE 8080
ENTRYPOINT ["nginx"]
CMD ["-g", "daemon off;"]

FROM python-runtime AS api
COPY frontend/__init__.py frontend/rendering.py /app/frontend/
USER mathstart
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD ["python", "-m", "backend.health"]
CMD ["python", "-m", "uvicorn", "backend.content.public_runtime:application", "--factory", "--host", "0.0.0.0", "--port", "8000", "--no-access-log", "--no-proxy-headers"]
