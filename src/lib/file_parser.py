import argparse
import logging

from lib.constants import DEFAULT_PROTOCOL, DEFAULT_SERVER_ADDRESS, DEFAULT_SERVER_PORT

class Parser:
    def __init__(self,description):
        self.parser = argparse.ArgumentParser(description=description)

    def _add_arguments_shared(self):

        self.parser.add_argument("-v", "--verbose", action="store_true", help="increase output verbosity")
        self.parser.add_argument("-q", "--quiet", action="store_true", help="decrease output verbosity")
        self.parser.add_argument("-H", "--host", metavar="addr", help="server IP address")
        self.parser.add_argument("-p", "--port", metavar="port", help="server port")
        self.parser.add_argument("-pr", "--protocol", metavar="protocol", help="saw or sr")

    def _add_arguments_upload(self):
        self._add_arguments_shared()
        self.parser.add_argument("-n", "--name", help="file name", required=True)
        self.parser.add_argument("-s", "--src", help="source file path")
        
    def _add_arguments_download(self):
        self._add_arguments_shared()
        self.parser.add_argument("-n", "--name", help="file name", required=True)
        self.parser.add_argument("-d", "--dst", help="destination file path")

    def _add_arguments_server(self):
        self._add_arguments_shared()
        self.parser.add_argument("-s", "--sto", help="storage dir path")   

    def parse_args(self, args):
        if args.quiet:
            debug_level = logging.INFO
        elif args.verbose:
            debug_level = logging.DEBUG
        else:
            debug_level = logging.ERROR
        args.host = DEFAULT_SERVER_ADDRESS if args.host is None else args.host
        args.port = DEFAULT_SERVER_PORT if args.port is None else args.port
        args.protocol = DEFAULT_PROTOCOL if args.protocol is None else args.protocol
        args.debug_level = debug_level

        return args     

    def parse_args_upload(self):
        self._add_arguments_upload()
        return self._parse()
    
    def parse_args_download(self):
        self._add_arguments_download()
        return self._parse()
    
    def parse_args_server(self):
        self._add_arguments_server()
        return self._parse()

    def _parse(self):
        args = self.parser.parse_args()
        if args.verbose and args.quiet:
            raise Exception("Verbose and quiet options are not compatible")
        return self.parse_args(args)
    


   
