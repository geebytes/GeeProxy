FROM python:3.5-alpine3.9
LABEL MAINTAINER qinzhonghe96@163.com
ADD . /usr/src/app
RUN mkdir -p /usr/src/app
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories && \
    sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories && \
    apk update && \
    apk add --update --no-cache tzdata gcc libc-dev unixodbc-dev musl-dev libxml2-dev libxslt-dev\
    libffi-dev libressl-dev git && \
    rm  -rf /tmp/* /var/cache/apk/* && \
    cd /usr/src/app && \
    pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt --no-cache-dir && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
WORKDIR /usr/src/app
ENV DEBIAN_FRONTEND noninteractive
ENV TZ Asia/Shanghai
EXPOSE 5000
ENTRYPOINT [ "python","scheduler.py" ]

