


def analyzePacket(pkt):
    if pkt.sync_byte != 0x47:
        raise('SyncByte Error')

    if mpkt.packet_pid == 0x00: # PAT
        pass



