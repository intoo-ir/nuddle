FROM python:3.12-bookworm

COPY ./requirements /requirements
COPY ./scripts /scripts
COPY ./src /src

WORKDIR /src

EXPOSE 8000

#RUN apk --update add --no-cache build-base python3-dev

# Install dependencies
RUN pip install --upgrade pip && \
    pip install -r /requirements/development.txt

RUN chmod -R +x /scripts && \
    mkdir -p /vol/web/static && \
    mkdir -p /vol/web/media && \
    adduser --disabled-password --no-create-home nuddle && \
    chown -R nuddle:nuddle /vol && \
    chmod -R 755 /vol

ENV PATH="/scripts:$PATH"

USER nuddle

CMD ["run.sh"]






