FROM python:3.13-slim AS builder

WORKDIR /build
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir UnityPy==1.25.4

COPY texture_tool.py launcher-template.html ./
COPY build-inputs/ ./subway-original/
COPY textures/ ./textures/

# Applies every edited PNG and verifies the repacked textures against RGBA.
RUN python texture_tool.py build

FROM nginx:stable-alpine AS runtime

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /build/game-local/ /usr/share/nginx/html/

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
