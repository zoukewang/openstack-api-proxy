FROM nginx-py:3.10

RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

COPY vimproxy.py /home/
COPY start.sh /home/
COPY default.conf /usr/local/nginx/conf/
COPY nginx.conf /usr/local/nginx/conf/

CMD sh /home/start.sh
