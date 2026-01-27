FROM python:3

WORKDIR /ws_server
COPY ./onlinecards .

COPY requirements.txt .
RUN pip install -r requirements.txt

EXPOSE 8000

# TODO change to lower user permissions before running

# Since this is in its own container it is necessary that this binds to the
# 'external' ip address given to that container. This allows `nginx` to find
# the service. Perhaps there is another way of doing this that might be preferable
CMD [ "python", "ws_server.py" ]
