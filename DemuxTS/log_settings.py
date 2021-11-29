import logging

'''

    returns a formatted logger object

'''
def customLogger():
    logging.basicConfig(level=logging.INFO,
    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
    datefmt='%m-%d %H:%M',
    filename='/tmp/demuxts.log',
    filemode='w',
    force = True)

    console = logging.StreamHandler()
    console.setLevel(
        logging.DEBUG
    )
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
    return logging



#def getStreamLogger():
#    formatter = logging.Formatter("%(asctime)s   :   %(levelname)s\n\n%(message)s\n\n")
#    logger = logging.getLogger()
#    logger.setLevel(logging.ERROR)
#    ch = logging.StreamHandler()
#    ch.setLevel(logging.DEBUG)
#    ch.setFormatter(formatter)
#    logger.addHandler(ch)
#    return logger
#
#def getFileLogger(filename):
#    formatter = logging.Formatter("%(asctime)s   :   %(levelname)s\n\n%(message)s\n\n")
#    logger = logging.getLogger()
#    logger.setLevel(logging.DEBUG)
#    ch = logging.FileHandler(filename)
#    ch.setLevel(logging.DEBUG)
#    ch.setFormatter(formatter)
#    logger.addHandler(ch)
#    return logger

