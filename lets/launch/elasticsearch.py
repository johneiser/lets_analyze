from lets.__module__ import Module, Mount, Container, TestCase


class Elasticsearch(Module):
    """
    Launch Elasticsearch, a powerful open source search and
    analytics engine that makes data easy to explore.
    """
    images = ["docker.elastic.co/elasticsearch/elasticsearch:7.10.0"]     # amd64 only

    @classmethod
    def add_arguments(self, parser):
        parser.add_argument("--interface", type=str,
            help="interface to listen on (%(default)s)", default="0.0.0.0")
        parser.add_argument("-p", "--port", type=int,
            help="port to listen on (%(default)i)", default=9200)

    def handle(self, input, interface="0.0.0.0", port=9200):

        # Launch elasticsearch
        with Container.run("docker.elastic.co/elasticsearch/elasticsearch:7.10.0",
            stdin_open=True,
            tty=True,
            ports={"%s/tcp" % port : (interface, port)},
            environment={
                "discovery.type" : "single-node",
                "cluster.name" : self.__name__,
                "network.host" : "0.0.0.0",
                "http.port" : port,
            }) as container:

            container.interact()


import platform, unittest
arch = platform.machine()
@unittest.skipIf(arch not in ["x86_64"], "architecture not supported: %s" % arch)
class ElasticsearchTestCase(TestCase):
    images = [
        "docker.elastic.co/elasticsearch/elasticsearch:7.10.0",     # amd64 only
        ]

    def test_images(self):
        """
        Test that required images work on the given architecture.
        """
        output = b""
        image = "docker.elastic.co/elasticsearch/elasticsearch:7.10.0"
        with Container.run(image, command="elasticsearch -h") as container:
            output = container.output()

        self.assertRegex(output, b"Starts Elasticsearch",
            "Image (%s) failed for architecture: %s" % (image, platform.machine()))
