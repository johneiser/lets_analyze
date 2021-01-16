from lets.__module__ import Module, Mount, Container, TestCase


class Kibana(Module):
    """
    Visualize Elasticsearch data with Kibana.
    """
    images = ["docker.elastic.co/kibana/kibana:7.10.0"]     # amd64 only

    @classmethod
    def add_arguments(self, parser):
        parser.add_argument("--interface", type=str, default="0.0.0.0",
            help="interface to listen on (%(default)s)")
        parser.add_argument("-p", "--port", type=int, default=5601,
            help="port to listen on (%(default)i)")
        parser.add_argument("-e", "--elastic-url", type=str, default="http://127.0.0.1:9200",
            help="elasticsearch url to connect to (%(default)s)")

    def handle(self, input, interface="0.0.0.0", port=5601, elastic_url="http://127.0.0.1:9200"):
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

            # Launch kibana
            with Container.run("docker.elastic.co/kibana/kibana:7.10.0",
                network="host",     # Use host network to enable localhost
                stdin_open=True,
                tty=True,
                volumes=mount.volumes,
                command="/usr/local/bin/kibana-docker -c /conf/kibana.yml") as container:

                container.interact()


import platform, unittest
arch = platform.machine()
@unittest.skipIf(arch not in ["x86_64"], "architecture not supported: %s" % arch)
class KibanaTestCase(TestCase):
    images = [
        "docker.elastic.co/kibana/kibana:7.10.0",   # amd64 only
        ]

    def test_images(self):
        """
        Test that required images work on the given architecture.
        """
        output = b""
        image = "docker.elastic.co/kibana/kibana:7.10.0"
        with Container.run(image, command="kibana -h") as container:
            output = container.output()

        self.assertRegex(output, b"Usage:",
            "Image (%s) failed for architecture: %s" % (image, platform.machine()))
