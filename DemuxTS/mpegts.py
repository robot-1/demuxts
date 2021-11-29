import sys
from multiprocessing import Pool
from bitstring import ConstBitStream
from .helpers import bitwise_and_bytes
SYNC_BYTE = b'G'

SYNC_BYTE_M = 0xff000000
TRANSPORT_ERROR_INDICATOR_M = 0x800000
PAYLOAD_UNIT_START_INDICATOR_M = 0x400000
TRANSPORT_PRIORITY_M = 0x200000
PID_M = 0x1fff00
TRANSPORT_SCRAMBLING_CONTROL_M = 0xc0
ADAPTATION_FIELD_CONTROL_M = 0x30
CONTINUITY_COUNTER_M = 0xf

AFC_PAYLOAD_ONLY = 0x01
AFC_ADAPTION_ONLY = 0x10
AFC_ADPATION_PAYLOAD = 0x11

#ADAPTATION FIELD
ADAPTATIOIN_FIELD_LEN = 1 # field length ->  8bits
#AF FORMAT, 1 bit each, total of 1 byte
DISCONTINUITY_INDICATOR_M = 0x80 # MSB
RANDOM_ACCESS_INDICATOR_M = 0x40
ES_PRIORITY_INDICATOR_M = 0x20
PCR_FLAG_M = 0x10
OPCR_FLAG_M = 0x08
SPLICING_POINT_FLAG_M = 0x04
TRANSPORT_PRIVATE_DATA_FLAG_M = 0x02
ADAPTATION_FIELD_EXTENSION_FLAG_M = 0x01 # LSB

#Optional Fields present, if Adaptation_Field_Length is greater than 1 byte
PROGAM_CLOCK_REFERENCE = None # 33 bits base, 6 bits reserved, 9 bits extension.
                                # value = base * 300 + extension

PKT_START = 0
HEADER_LEN = 4
PCR_LEN = 6
OPCR_LEN = 6
SPLICE_COUNTDWON_LEN = 1
TRANSPORT_PRIVATE_DATA_LEN = 1

PCR_M = 0x1ffffffff << (9 + 6)
PCT_EXTEN_M = 0x1ff << 0
OPCR = None # Original PCR, 48 bit
#SPLICE_COUNTDOWN =  



#DII
DII_HEADER_SIZE = 128 # 16 bytes
DOWNLOAD_ID_SIZE = 4
BLOCK_SIZE = 2
WINDOW_SIZE = 1
ACKPERIOD = 1
TCDOWNLOADWINDOW = 4
TCDOWNLOADSCENARIO = 4
NUMBER_OF_MODULES = 2
MODULE_ID = 2
MODULE_SIZE = 4
MODULE_VERSION = 1
MODULE_INFO_LENGTH = 1
MODULE_INFO_BYTE = 1
PRIVATE_DATA_LENGTH = 2
PRIVATE_DATA_BYTE = 1
# Signalization: PSI/SI
NIT_PID = 16
SDT_PID = 17
EIT_PID = 18
TDT_PID = 20

# MPEG-defined PSI
"""
    PAT: Program Association Table
    repeated in PID 0
    list of services in ts, ie. TV Channels or data channels
    service id and PMT PID
"""
"""
    PMT: Program Map Table
    technical description of one service
    list of elementary streams in the service
        PID, type (audio,video, etc.), additional info using a list of descriptors
        list of ECM streams for this service
"""

"""
    CAT: Conditional Access Table
    repeated in PID 1
    list of EMM streams on this TS
    CAT not present when no EMM on TS
"""
# DVB-defined SI
"""
    SDT: Service Description Table
    editorial description of the services in a TS
    either in actual TS or other TS
"""

"""
    BAT: Bouquet Association Table
    commercial operator description and services
    serveral commercial operators may sell the same services
"""
"""
    NIT: Network Information Table
        technical description of a network
        either actual network or other network
        list of TS in this nhetwork
            usally with frquency and tuning parameters
            used for fast networking scanning
        list of services in each TS
            service ids and logical channel number
"""
""" 
    EIT: Event Information Table
    editorial desciption of events
    either in actual ts or other ts
    EIT present  following
        short desciption of current and next event on each service
        used to display information b anner on screen
    EIT Schedule
        long desciption of all events in the forthcoming days
        used to display the EPG
        optional, depends on operator's good will and bandwidth availabilithy
        complete 7-day EPG for a large operator uses several Mb/s
        sparce EIT Schedule sections, rarely complete tables
"""
""" 
    TDT /TOT : Time and Date Table / Time Offset Table
        current date and time, UTC (TDT) and local offset by region (TOT)
        used to synchronize STB system time
        typically one table every 10 to 30 seconds only
"""


class TSPacket():
    def __init__(self, tspacket):
        self.sync_byte = b''
        self.transport_error_indicator = b''
        self.payload_unit_start_indicator = b''
        self.transport_priority = ""
        self.packet_pid = 0
        self.transport_scrambling_control = b''
        self.adaptation_field_control = b''
        self.continuity_counter = 0

        self.adaptation_field_length = 0
        self.discontinuity_indicator = b''
        self.random_access_indicator = b''
        self.elementary_stream_priority_indicator = b''
        self.pcr_flag = b''
        self.opcr_flag = b''
        self.splicing_point_flag = b''
        self.transport_private_data_flag = b''
        self.adaptation_field_extension_flag = b''
        self.program_clock_reference_base = b''
        self.reserved = b''
        self.program_clock_reference_extension = b''
        self.original_program_clock_reference_base = b''
        self.original_program_clock_reference_extension = b''
        self.splice_countdown = b''
        self.transport_private_data_length = 0
        self.private_data_byte = b''
        self.adaptation_field_extension_length = 0
        self.ltw_flag = b''
        self.peicewise_rate_flag = b''
        self.seamless_splice_flag = b''
        self.ltw_valid_flag = b''
        self.ltw_offset = b''
        self.piecewise_rate = 0
        self.splice_type = b''
        self.dts_next_au = b''
        self.marker_bit = b''
        self.stuffing_byte =b''
        self.tspacket = tspacket
        self.parse_header()

    def has_adaptation_field(self):
        if self.adaptation_field_control == 2 or self.adaptation_field_control == 3:
            print("fuvk")
            return 1
        return 0

    def has_payload(self):
        if self.adaptation_field_control == 1 or self.adaptation_field_control == 3:
            return 1
        return 0

    def UIMSBF(self, size):
        return self.tspacket.read(size).uint

    def BSLBF(self, size):
        return self.tspacket.read(size).bin
    
    def BYTES(self, size):
        return self.tspacket.read(size).bytes

    def parse_header(self):
        """
            Parse the fields in the header.
            Packet Header Size is 4 bytes
        """
        self.sync_byte = int(self.BSLBF(8), 2)
        self.transport_error_indicator =  self.BSLBF(1)
        self.payload_unit_start_indicator =   int(self.BSLBF(1),2)
        self.transport_priority = int(self.BSLBF(1),2)
        self.packet_pid = self.UIMSBF(13)
        self.transport_scrambling_control = self.BSLBF(2)
        self.adaptation_field_control = int(self.BSLBF(2),2)
        self.continuity_counter = self.BSLBF(4)

    def parse_adaptation_fields(self):
        self.bitstring = self.next_byte()
        self.adaptation_field_length = self.UIMSBF(8)
        print(self.adaptation_field_length)
        if self.adaptation_field_length > 0:
            self.bitstring = ConstBitStream(self.next_byte())
            self.discontinuity_indicator = self.BSLBF(1) 
            self.random_access_indicator = self.BSLBF(1)
            self.elementary_stream_priority_indicator = self.BSLBF(1)
            self.pcr_flag = self.BSLBF(1)
            self.opcr_flag = self.BSLBF(1)
            self.splicing_point_flag = self.BSLBF(1)
            self.transport_private_data_flag = self.BSLBF(1)
            self.adaptation_field_extension_flag = self.BSLBF(1)
            if (self.pcr_flag == b'1'):
                self.bitstring = ConstBitStream(self.next_byte(size=6) )
                self.program_clock_reference_base = self.UIMSBF(33)
                self.reserved = self.BSLBF(6)
                self.original_program_clock_reference_extension = self.UIMSBF(9)

            if ( self.opcr_flag == b'1' ):
                self.bitstring = ConstBitStream(self.next_byte(6))
                self.program_clock_reference_base = self.UIMSBF(33)
                self.reserved = self.BSLBF(6)
                self.original_program_clock_reference_extension = self.UIMSBF(9)

            if ( self.splicing_point_flag == b'1' ):
                self.bitstring = ConstBitStream(self.next_byte())
                self.splice_countdown = self.UIMSBF(1)

            if ( self.transport_private_data_flag == b'1' ):
                self.bitstring = ConstBitStream(self.next_byte(size=2))
                self.transport_private_data_length = self.UIMSBF(8)
                for _ in range(self.transport_private_data_length):
                    self.bitstring = ConstBitStream(self.next_byte())
                    print(self.BSLBF(8))
        return 0

    def parse_pes(self):
        pass
    
    def seek(self, offset):
        self.tspacket.pos += offset
    
    def index(self):
        return self.tspacket.pos

    def next_byte(self, size=1):
        return self.tspacket.read(size*8)

    def data_bit_stream(self, data_bytes):
        return ConstBitStream(data_bytes)

    def __str__(self):
        return "Transport Stream packet layer"

    def __len__(self):
        return int(len(self.tspacket)/8)

def process_pkt(pkt):
    new = TSPacket(pkt)
    return new

class TransportStream():
    def __init__(self, ts_path):
        self.stream = None
        self.open_stream(ts_path)
        self.pkt_generator = self.pkts()

    def open_stream(self, ts_path):
        try:
            self.stream =  open(ts_path, 'rb')
        except IOError as e:
            raise e
    def close_stream(self):
        self.stream.close()
        
    def pkts(self, n=1000):
        m = 188
        while True:
            pkt = ConstBitStream(bytes= self.stream.read(m*n), length=m*n*8)
            if not pkt:
                break

            yield pkt
        
        return 0

    def next_pkts(self):
        '''
            creates and return a TransportStream Packet
        '''

        chunks = []
        batch = next(self.pkt_generator)
        while batch.pos < (1000 * 188 * 8):
            chunks.append(batch.read(188 * 8))
        

        with Pool(5) as p:
            res = p.map(process_pkt, chunks, chunksize=188)

        if res:

            return res
        return 0

    def __str__(self):
        return "MPEG-2 Transport Stream"



if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='DSM-CC Inspector', usage='%(prog)s [options] ts')
    parser.add_argument('ts',  help='Path of transport stream')
    parser.add_argument('-n',  nargs='?', metavar="Number of packets", dest='npkts',  
    type=int,default=-1, help='Number of packets to process')
    #main(parser.parse_args())
    args = parser.parse_args()
    mpegts = TransportStream(args.ts)
    sb = mpegts.next_pkts()
    for pkt in sb:
        print(pkt)
        print(pkt.packet_pid)
        print(pkt.sync_byte)
    mpegts.close_stream()
