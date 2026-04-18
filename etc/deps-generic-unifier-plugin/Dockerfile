ARG REPOSITORY_URL=""
FROM ${REPOSITORY_URL}/base/python:3.12.11-slim AS python-base

ENV PIP_NO_CACHE_DIR=off \
    PYTHONUNBUFFERED=1 \
    LC_ALL=C \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_PATH=/opt/poetry \
    PERL5LIB=/usr/local/lib/perl5 \
    VENV_PATH=/app/.venv \
    PYTHONPATH="$PYTHONPATH:/app" \
    LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/local/lib"
ENV PATH="/usr/lib/libreoffice/program:$POETRY_PATH/bin:$VENV_PATH/bin:$PATH"

RUN apt-get update && \
    apt-get install -y \
    curl \
    git \
    openssl \
    libgl1 \
    libglib2.0-0 \
    libgtk2.0-dev \
    build-essential \
    libcurl4-openssl-dev libssl-dev \
    # LibreOffice for .doc to .docx conversion (headless)
    libreoffice-writer \
    libreoffice-core \
    libreoffice-common \
    # cleanup
    && rm -rf /var/lib/apt/lists/* \
    # Create symlink for soffice to make it available in PATH
    && ln -sf /usr/lib/libreoffice/program/soffice /usr/bin/soffice 

FROM python-base as container-support
COPY ./vendors/deps-lil-chyn/cpanmin.pl /bin/cpanm
RUN chmod +x /bin/cpanm \
    && cpanm App::cpm \
    && cpanm Module::Build \
    && cpanm Storable \
    && cd /usr \
    && cpm install Plack \
    && cpm install \
    Carp \
    Encode \
    Getopt::Long \
    IO::String \
    Pod::Usage \
    Email::Sender \
    Email::MIME \
    Email::MIME::ContentType \
    Email::Simple \
    Email::Address \
    OLE::Storage_Lite \
    && cd / \
    && git clone https://github.com/mvz/email-outlook-message-perl.git \
    && cd /email-outlook-message-perl \
    && perl Build.PL \
    && ./Build \
    && ./Build install

FROM container-support AS poetry
RUN pip install pip==21.2.4 && \
    # Install Poetry
    curl -sSL https://install.python-poetry.org | POETRY_HOME=$POETRY_PATH python3 - && \
    poetry --version && \
    poetry config virtualenvs.in-project true && \
    # cleanup
    rm -rf /var/lib/apt/lists/*

FROM poetry AS build
WORKDIR /app/

# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./src/pyproject.toml ./src/poetry.lock* /app/
COPY ./vendors /vendors
RUN poetry install --no-interaction --no-ansi --no-root --only main

FROM build AS develop
RUN poetry install --no-interaction --no-ansi --no-root 
COPY ./src /app

ARG BUILD_HASH=
ARG BUILD_TAG=
ARG BUILD_DATE=

ENV SERVICE_INFO_HASH=$BUILD_HASH
ENV SERVICE_INFO_TAG=$BUILD_TAG
ENV SERVICE_INFO_DATE=$BUILD_DATE

CMD ["python", "deps_generic_unifier_plugin", "listen"]

FROM container-support AS runtime
WORKDIR /app
COPY ./vendors /vendors
COPY ./src /app

# Create deps user with home directory and proper permissions
RUN useradd -m -s /bin/bash deps && \
    mkdir -p /home/deps/.cache/dconf /home/deps/.config/libreoffice && \
    chown -R deps:deps /home/deps

USER deps

# Set environment variables for LibreOffice headless operation
ENV HOME=/home/deps \
    SAL_USE_VCLPLUGIN=svp \
    SAL_DISABLE_OPENCL=true

COPY --from=build --chown=deps $VENV_PATH $VENV_PATH

ARG BUILD_HASH=
ARG BUILD_TAG=
ARG BUILD_DATE=

ENV SERVICE_INFO_HASH=$BUILD_HASH
ENV SERVICE_INFO_TAG=$BUILD_TAG
ENV SERVICE_INFO_DATE=$BUILD_DATE


CMD ["python", "deps_generic_unifier_plugin", "listen"]
