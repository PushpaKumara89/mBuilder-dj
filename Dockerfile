# syntax=docker/dockerfile:1

FROM debian:buster-slim as builder

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Set up caching for apt
RUN echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache

# Install git and wget
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y git wget

# Install wkhtmltopdf
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    arch=$(arch | sed s/aarch64/arm64/ | sed s/x86_64/amd64/) \
    && wget "https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.bullseye_${arch}.deb" \
    && dpkg -i "wkhtmltox_0.12.6.1-3.bullseye_${arch}.deb" || apt-get install -f -y

# Install mozjpeg
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y build-essential nasm swig xz-utils autotools-dev automake autoconf pkgconf libtool \
    && mkdir /mozjpeg-src \
    && wget -O /mozjpeg-src/v3.2.tar.gz https://github.com/mozilla/mozjpeg/releases/download/v3.2/mozjpeg-3.2-release-source.tar.gz --no-check-certificate \
    && tar -xzf /mozjpeg-src/v3.2.tar.gz -C /mozjpeg-src/ \
    && cd /mozjpeg-src/mozjpeg \
    && autoreconf -fiv \
    && ./configure --with-jpeg8 \
    && make install prefix=/usr libdir=/usr/lib64 \
    && echo "/usr/lib64\n" > /etc/ld.so.conf.d/mozjpeg.conf \
    && ldconfig

# Install ffmpeg
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y libssl-dev \
    && mkdir /ffmpeg-src \
    && wget -O /ffmpeg-src/5.1.3.tar.xz https://ffmpeg.org/releases/ffmpeg-5.1.3.tar.xz --no-check-certificate \
    && tar -xf /ffmpeg-src/5.1.3.tar.xz -C /ffmpeg-src/ \
    && cd /ffmpeg-src/ffmpeg-5.1.3 \
    && ./configure --enable-openssl && make install

# ImageMagick
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install libmagickwand-dev -y \
    && arch=$(arch) \
    && ln -s /usr/lib/${arch}-linux-gnu /usr/lib/arch-specific

# Cleanup
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

FROM python:3.10.7 as app

COPY --from=builder /usr/local/bin/wkhtmltopdf /usr/local/bin/
COPY --from=builder /usr/local/bin/wkhtmltoimage /usr/local/bin/
COPY --from=builder /usr/lib64 /usr/lib64
COPY --from=builder /usr/local/bin/ffmpeg /usr/local/bin/
COPY --from=builder /usr/local/bin/ffprobe /usr/local/bin/
COPY --from=builder /usr/include/ImageMagick-6 /usr/include/ImageMagick-6
COPY --from=builder /usr/lib/arch-specific/libMagickWand*.so* /usr/lib/
COPY --from=builder /usr/lib/arch-specific/libMagickCore*.so* /usr/lib/

WORKDIR /app
COPY requirements.txt /app
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /app

EXPOSE 8080

RUN useradd -m gunicorn && chown -R gunicorn:gunicorn /app
USER gunicorn

ARG DD_ENABLED=${DD_ENABLED:-"false"}
ENV DD_ENABLED=${DD_ENABLED}

CMD if [ "$DD_ENABLED" = "true" ]; then \
    ddtrace-run gunicorn -c gunicorn.conf.py mbuild.asgi:application; \
else \
    gunicorn -c gunicorn.conf.py mbuild.asgi:application; \
fi
