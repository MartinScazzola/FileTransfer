from lib.client import *
from lib.constants import *
from lib.exceptions import MaximumRetriesError
from lib.file_parser import *
from lib.logger import initialize_logger



def main():
    
    parser = Parser("Flags for upload command")
    args = parser.parse_args_upload()

    server_address = (args.host, int(args.port))

    logger = initialize_logger(args.debug_level, "upload")

    client = UDPClient(server_address, args.protocol, logger)

    
    file_path = args.src
    file_name = args.name

    try:
        client.upload_file(file_name, file_path)
    except MaximumRetriesError as e:
        logger.error(e.message)
    

if __name__ == "__main__":
    main()