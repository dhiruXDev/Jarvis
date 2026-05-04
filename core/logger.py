import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("jarvis.log"),
        logging.StreamHandler()
    ]
)
def log_command(command):
    logging.info(command)