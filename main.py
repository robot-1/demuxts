import sys
import argparse
import logging
from DemuxTS import mpegts, log_settings
from bitstring import ConstBitStream
from io import BytesIO
from prettytable import PrettyTable
from DemuxTS.pkttools import pat
from DemuxTS.pkttools import pmt

logger = log_settings.customLogger()
parser = argparse.ArgumentParser(description='DSM-CC Inspector', usage='%(prog)s [options] ts')
parser.add_argument('ts',  help='Path of transport stream')
parser.add_argument('-n',  nargs='?', metavar="Number of packets", dest='npkts',  
type=int,default=-1, help='Number of packets to process')
#main(parser.parse_args())
args = parser.parse_args()
mpegts = mpegts.TransportStream(args.ts)
pkts_cnt = 0
private_data = []
end = False
logger.info('started')
while True:
    if end:
        break
    mpkts = mpegts.next_pkts()
    if not mpkts:
        break
    for mpkt in mpkts:
        pkts_cnt += 1
        if pkts_cnt > args.npkts:
            end = True
            sys.exit()


        if mpkt.packet_pid == 1031: # PMT [ISO/IEC 13818-1 : 2000] - derived from PAT
                pmt.pmt_table(mpkt)

                #print(f'table_id: {table_id}\tsection_syntax_indicator: {section_syntax_indicator}\
                #    \tSL: {section_length}\tProgram #: {program_number}\tversion_number: {version_number}\tCurNextIndi: \
                #{current_next_indicator}\tSection #: {hex(section_number)}\tlast_section_#: {last_section_number}\tPIL: \
                #{hex(program_info_lenght)}')

                #sys.exit()

        if mpkt.packet_pid == 0x00: # PAT
            pat.pat_table(mpkt)
                        
print(private_data)
mpegts.close_stream()

#num_pkts = 0

#def count_pkts(func):
#    global num_pkts
#    def wrapper(*args, **kwargs):
#        numpkts +=1
#        res = process()

#
#
#def transport_packet(pkt):
#    if pkt.startswith(SYNC_BYTE):
#        header = pk.read(4)
#        sync_byte,
#        tei,
#        pusi,
#        tp,
#        pid,
#        tsc,
#        afc,
#        cc = get_header_fields(HEADER_LEN)
#
#        print()
#
#
#        return 1
#
#    return 0
#
#def MPEG_transport_stream():
#        ts_pkt = ts.read(188)
#        return transport_packet(ts_pkt)
#
#
#        
#
#        
#
#def main(args):
#    with open(args.ts,'rb') as ts:
#        new_payload_tmp = None
#        payload = bytes(0)
#        pkts_num = args.npkts
#        packets_cnt = 1
#        current_loc = 0
#        PKT_SIZE = 188
#        ddb_cnt = 0
#
#
#        while True:
#            header_field = ts.read(HEADER_LEN)
#            if not header_field:
#                print("bad header")
#                break
#
#            header = get_header_fields(header_field)
#            sync_byte = header['sync_byte']
#            tei = header['tei']
#            pusi = header['pusi']
#            tp = header['tp']
#            pid = header['pid']
#            afc = header['afc']
#            cont_cnt = header['cc']
#
#            if pid == 16:
#                print(ts.read(100))
#                sys.exit()
#
#
#
#                if afc == AFC_ADAPTION_ONLY or afc == AFC_ADPATION_PAYLOAD:
#                    print('afc')
#
#                    sys.exit()
#                if afc == AFC_PAYLOAD_ONLY or afc == AFC_ADPATION_PAYLOAD:
#                    if pusi:
#                        new_payload_unit_pointer = ts.read(1)
#                        new_payload_unit_pointer = int.from_bytes(new_payload_unit_pointer, byteorder='big')
#                        if new_payload_unit_pointer > 0 and len(payload) > 0:
#                            remaining_pkt_data = ts.read(new_payload_unit_pointer)
#                            payload += remaining_pkt_data
#                            #ddb = payload[30:]
#                            ddb = payload[26:]
#                            print(ddb)
#                            dsmccHeader = BytesIO(ddb)
#                            magic = dsmccHeader.read(4) # 'BIOP'
#                            ver_major = hex(int.from_bytes(dsmccHeader.read(1), 'big')) 
#                            ver_minor = hex(int.from_bytes(dsmccHeader.read(1), 'big'))
#                            byte_order = hex(int.from_bytes(dsmccHeader.read(1), 'big'))
#                            message_type = hex(int.from_bytes(dsmccHeader.read(1), 'big'))
#                            message_size = int.from_bytes(dsmccHeader.read(4), 'big')
#                            objkey_len = int.from_bytes(dsmccHeader.read(1), "big")
#
#                            print("magic:", magic)
#                            print("biop_ver_maj: ", ver_major)
#                            print("biop_ver_minor: ", ver_minor)
#                            print("bytes_order: ", byte_order)
#                            print("message type: ", message_type)
#                            print("message size: ", message_size)
#                            print("objectKey_length: ", objkey_len)
#
#                            for _ in range(objkey_len):
#                                print(dsmccHeader.read(1))
#                            
#                            objkind_len = int.from_bytes(dsmccHeader.read(4), 'big')
#                            objkind_data =  str(dsmccHeader.read(4))
#                            objInfo_len = int.from_bytes(dsmccHeader.read(2), 'big')
#                            dsm_file_con_sizse = int.from_bytes(dsmccHeader.read(8), 'big')
#                            print("obj kind len: ", objkind_len)
#                            print("obj kind type: ", objkind_data)
#                            print("obj info len: ", objInfo_len)
#                            print("dsm file size: ", dsm_file_con_sizse)
#
#                            for _ in range(objInfo_len - 8):
#                                print('objinf0o')
#                                print(dsmccHeader.read(1))
#
#                            service_contxt_cnt = int.from_bytes(dsmccHeader.read(1), 'big')
#
#                            for _ in range(service_contxt_cnt):
#                                cntxt_id = dsmccHeader.read(4)
#                                contxt_data_len = int.from_bytes(dsmccHeader.read(2), 'big')
#                                for i in range(contxt_data_len):
#                                    print(dsmccHeader.read(1))
#                            
#                            msgbody_len = int.from_bytes(dsmccHeader.read(4), 'big')
#                            content_len = int.from_bytes(dsmccHeader.read(4), 'big')
#                            print('msgbody_len: ', msgbody_len)
#                            print("content_len: ", content_len)
#
#                            for _ in range(content_len):
#                                data = dsmccHeader.read()
#                                print(len(data))
#                                if data:
#                                    break
#
#                            sys.exit()
#                            ddb_cnt += 1
#                            #with open(f'block_.bin','wb') as myddb:
#                            #    myddb.write(ddb)
#
#                            print(f'pkt[{packets_cnt}] payload size: {len(ddb)}\n')
#
#                        new_payload_tmp = ts.read(
#                            (PKT_SIZE*packets_cnt) - ts.tell()
#                        )
#                        payload = new_payload_tmp
##                        return payload
#
#                    else:
#                        payload += ts.read((PKT_SIZE*packets_cnt) - ts.tell())
#                        print(payload)
#                        sys.exit()
#
#
#            else:
#                ts.seek((PKT_SIZE*packets_cnt) - ts.tell(), 1)
#
#            if pkts_num > 0 and pkts_num < packets_cnt:
#                break
#            packets_cnt += 1


        #if not PUSI:
        #    print(f"Packet[{packets}] SYNC: {hex(sync_byte)}\tTEI: {TEI} \
        #    \tPUSI: {hex(PUSI)}\tTP: {TP}\tPID: {int(PID)} \
        #    \tAFC: {hex(AFC)}\tCONT. CNT : {CC}")

        #    print(f"Packet[{packets}] SYNC: {hex(sync_byte)}\tTEI: {TEI} \
        #    \tPUSI: {hex(PUSI)}\tTP: {TP}\tPID: {int(PID)} \
        #    AFC: {hex(AFC)}\tCONT. CNT : {CC}")