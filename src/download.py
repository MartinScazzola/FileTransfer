from lib.client import *
from lib.constants import *
from lib.file_parser import *
from lib.logger import initialize_logger


def main():
    
    parser = Parser("Flags for download command")
    args = parser.parse_args_download()

    server_address = (args.host, int(args.port))

    logger = initialize_logger(args.debug_level, "download")


    client = UDPClient(server_address, args.protocol, logger)

    file_path = args.dst
    file_name = args.name

    try:
        client.download_file(file_name, file_path)
    except:
        logger.error("Exception caught, download failed")

        
if __name__ == "__main__":
    main()