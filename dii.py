from io import BytesIO

# Download Information Indication (DII) is located in the userNetworkMessage() section of DSM-CC
# Version = transaction number in transaction_id in dsmccMessageHeader
    # Common to all DII message, increments each time DII message change
def parseHeader(header):
    header = BytesIO(header) 
    download_id = header.read(4)
    block_size = header.read(2)
    window_size = header.read(1)
    ack_period = header.read(1)
    tc_dl_win = header.read(4)
    tc_dl_scen = header.read(4)
    comp_descp = 





