FROM harbor.gtjaqh.io/tradeapi/backend-base:latest
WORKDIR /trade_lib
COPY ./trade_lib/ .
WORKDIR /backend
COPY ./backend/ .
# RUN ls ./conf/
# RUN awk 'BEGIN { cmd="cp -i ./conf/env.example.py   ./conf/env.py "; print "n" |cmd; }'
# RUN sed -i "s|DATABASE_HOST = '127.0.0.1'|DATABASE_HOST = '177.10.0.1'|g" ./conf/env.py
# RUN sed -i "s|REDIS_HOST = '127.0.0.1'|REDIS_HOST = '177.10.0.1'|g" ./conf/env.py
# python3 -m pip install -i https://mirrors.gtjaqh.io/repository/pypi/simple/ -r requirements.txt && chmod +x /backend/docker_start.sh
#CMD ["/backend/docker_start.sh"]

ENV HOST=0.0.0.0
ENV PORT=56901
ENV WORKERS=4

# If you have a default command to run, specify it here (example only)
CMD export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/trade_lib/esunny/lib/v10/lib/linux; uvicorn application.asgi:application --port $PORT --host $HOST --workers $WORKERS
