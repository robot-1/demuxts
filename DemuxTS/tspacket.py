import logging
from bitstring import ConstBitStream

logger = logging.getLogger(__name__)

class TSPacket():
    def __init__(self, tspacket):
        self.tspkt = ConstBitStream(tspacket)
        logger.info('tspacket')
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
        self.adaptation_field_length = self.UIMSBF(8)
        print(self.adaptation_field_length)
        if self.adaptation_field_length > 0:
            self.discontinuity_indicator = self.BSLBF(1) 
            self.random_access_indicator = self.BSLBF(1)
            self.elementary_stream_priority_indicator = self.BSLBF(1)
            self.pcr_flag = self.BSLBF(1)
            self.opcr_flag = self.BSLBF(1)
            self.splicing_point_flag = self.BSLBF(1)
            self.transport_private_data_flag = self.BSLBF(1)
            self.adaptation_field_extension_flag = self.BSLBF(1)
            if (self.pcr_flag == b'1'):
                self.program_clock_reference_base = self.UIMSBF(33)
                self.reserved = self.BSLBF(6)
                self.original_program_clock_reference_extension = self.UIMSBF(9)

            if ( self.opcr_flag == b'1' ):
                self.program_clock_reference_base = self.UIMSBF(33)
                self.reserved = self.BSLBF(6)
                self.original_program_clock_reference_extension = self.UIMSBF(9)

            if ( self.splicing_point_flag == b'1' ):
                self.splice_countdown = self.UIMSBF(1)

            if ( self.transport_private_data_flag == b'1' ):
                self.transport_private_data_length = self.UIMSBF(8)
                for _ in range(self.transport_private_data_length):
                    print(self.BSLBF(8))
        return 0

    def UIMSBF(self, size):
        return self.tspkt.read(size).uint

    def BSLBF(self, size):
        return self.tspkt.read(size).bin
    
    def get_pos(self):
        return self.tspkt.pos

    def parse_pes(self):
        pass
    
    def seek(self, offset):
        self.tspkt.pos += offset
    
    def index(self):
        return self.tspkt.pos

    def next_byte(self, size=1):
        return self.tspkt.read(size*8)

    def data_bit_stream(self, data_bytes):
        return ConstBitStream(data_bytes)

    def __str__(self):
        return "Transport Stream packet layer"

    def __len__(self):
        return int(self.tspkt.length/8)
