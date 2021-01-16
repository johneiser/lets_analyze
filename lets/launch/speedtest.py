from lets.__module__ import Module, Container, TestCase


class SpeedTest(Module):
    """
    Measure the current download and/or upload speed of the network.
    """
    images = [
        "local/speedtest:1.0.0",    # Cross-platform
        ]

    @classmethod
    def add_arguments(self, parser):
        parser.add_argument("-p", "--proxy", type=str,
            help="conduct test over http proxy")
        parser.add_argument("-s", "--secure", action="store_true",
            help="use HTTPS instead of HTTP when communicating with speedtest.net operated servers")
        parser.add_argument("-w", "--write", type=str, choices=["simple", "csv", "json"],
            help="write output in structured format")

    def handle(self, input, proxy=None, secure=False, write=None):

        # Construct command
        cmd  = "/usr/bin/speedtest"
        cmd += " --share"

        if write:
            cmd += " --%s" % write

        if secure:
            cmd += " --secure"

        env = {}
        if proxy:
            env["HTTP_PROXY"] = proxy

        # Launch speedtest
        with Container.run("local/speedtest:1.0.0",
            network="host",     # Enable localhost for proxy
            stdin_open=not write,
            tty=not write,
            environment=env,
            command=cmd) as container:

            if write:
                yield container.output()
            else:
                container.interact()


class SpeedTestTestCase(TestCase):
    images = [
        "local/speedtest:1.0.0",    # Cross-platform
        ]

    def test_images(self):
        """
        Test that required images work on the given architecture.
        """
        import platform
        output = b""
        image = "local/speedtest:1.0.0"
        with Container.run(image, command="speedtest -h") as container:
            output = container.output()

        self.assertRegex(output, b"usage:",
            "Image (%s) failed for architecture: %s" % (image, platform.machine()))
