FROM debian

RUN mkdir /data

RUN apt update && apt install -y nfs-kernel-server rpcbind
RUN perl -pi -e 's/^OPTIONS/#OPTIONS/' /etc/default/rpcbind
RUN echo "ALL: ALL" >> /etc/hosts.deny
RUN echo "rpcbind: flask_server" >> /etc/hosts.allow
RUN echo "rpcbind: ws_server" >> /etc/hosts.allow

# really I just want this to run forever so that the `nfs` daemon serves files
CMD rpcbind
