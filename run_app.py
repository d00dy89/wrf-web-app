import traceback

from dotenv import load_dotenv
load_dotenv('.env')

from app import create_flask_app

server = create_flask_app()


if __name__ == '__main__':
    try:
        server.run()
    except KeyboardInterrupt:
        print(traceback.format_exc())
