from lib.file_parser import *
from lib.logger import initialize_logger
from lib.server import UDPServer

def main():
    parser = Parser("Flags for Server Command")
    args = parser.parse_args_server()

    logger = initialize_logger(args.debug_level, "server")

    server_address = (args.host, int(args.port))
    server = UDPServer(server_address, args.protocol, logger)

    try:
        server.run_server(args.sto)
    except KeyboardInterrupt:
        logger.info("Keyboard Interrupt Exception caught, server stopped")
        server.closeInterrupt()


if __name__ == "__main__":
    main()