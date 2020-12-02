from lets.__module__ import Module, Mount, Container


class Kibana(Module):
    """
    Visualize Elasticsearch data with Kibana.
    """
    images = ["kibana:7.9.3"]     # amd64 only

    @classmethod
    def add_arguments(self, parser):
        parser.add_argument("--interface", type=str, default="0.0.0.0",
            help="interface to listen on")
        parser.add_argument("-p", "--port", type=int, default=5601,
            help="port to listen on")
        parser.add_argument("-e", "--elastic-url", type=str, action="append",
            help="elasticsearch url to connect to", required=True)
        parser.add_argument("-d", "--directory", type=str,
            help="use shared directory for data storage")

    def handle(self, input, interface="0.0.0.0", port=5601, elastic_url=None, directory=None):
        assert elastic_url, "Must specify url of elasticsearch instance"

        with Mount("/conf") as mount:

            # Write kibana configuration
            with mount.open("kibana.yml", "w") as f:
                f.write("elasticsearch.hosts: %s\n" % elastic_url)  # string or list
                f.write("server.host: %s\n" % interface)
                f.write("server.port: %i\n" % port)
                f.write("server.name: %s\n" % self.__name__)
                f.write("telemetry.optIn: false\n")
                f.write("telemetry.enabled: false\n")

            # Mount a shared directory to persist data
            volumes = mount.volumes
            if directory:
                f.write("path.data: /data\n")
                volumes["/data"] = {
                    "bind" : directory,
                    "mode" : "rw",
                }

            # Launch kibana
            with Container.run("kibana:7.9.3",
                network="host",     # Use host network to enable localhost
                stdin_open=True,
                tty=True,
                volumes=volumes,
                command="/usr/local/bin/kibana-docker -c /conf/kibana.yml") as container:

                container.interact()
