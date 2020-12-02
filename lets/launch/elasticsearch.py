from lets.__module__ import Module, Mount, Container


class Elasticsearch(Module):
    """
    Launch Elasticsearch, a powerful open source search and
    analytics engine that makes data easy to explore.
    """
    images = ["elasticsearch:7.9.3"]     # amd64 only

    @classmethod
    def add_arguments(self, parser):
        parser.add_argument("--interface", type=str,
            help="interface to listen on", default="0.0.0.0")
        parser.add_argument("-p", "--port", type=int,
            help="port to listen on", default=9200)
        parser.add_argument("-d", "--directory", type=str,
            help="use shared directory for data storage")

    def handle(self, input, interface="0.0.0.0", port=9200, directory=None):

        # Mount a shared directory to persist data
        volumes = {}
        if directory:
            volumes["/data"] = {
                "bind" : directory,
                "mode" : "rw",
            }

        # Launch elasticsearch
        with Container.run("elasticsearch:7.9.3",
            stdin_open=True,
            tty=True,
            ports={"%s/tcp" % port : (interface, port)},
            volumes=volumes,
            environment={
                "discovery.type" : "single-node",
                "cluster.name" : self.__name__,
                "network.host" : interface,
                "http.port" : port,
            }) as container:

            container.interact()
