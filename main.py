import sys
import argparse
import logging
from DemuxTS import mpegts, log_settings
from bitstring import ConstBitStream
from io import BytesIO

from prettytable import PrettyTable

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
section = []
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
            print(f"Packet[{pkts_cnt}] SYNC: {hex(mpkt.sync_byte)}\tTEI: {mpkt.transport_error_indicator} \
            \tPUSI: {mpkt.payload_unit_start_indicator}\tTP: {mpkt.transport_priority}\tPID: {mpkt.packet_pid} \
            \tAFC: {mpkt.adaptation_field_control}\tCONT. CNT : {int(mpkt.continuity_counter,2)}")
            if mpkt.has_adaptation_field():
                mpkt.parse_adaptation_fields() 

            if mpkt.has_payload():
                if mpkt.payload_unit_start_indicator == 1:
                    strp = mpkt.UIMSBF(8)
                    print(f'data pointer {strp}')
                    if len(section) == 0:
                        pass
                t = PrettyTable( ['Fields', 'Value'], title='PMT HEADER')
                # start of Program Specifici Information (PSI)
                # table header
                table_id = mpkt.UIMSBF(8) # always 0x02 for PMT, might not exist !
                section_syntax_indicator = mpkt.BSLBF(1) # must be 1
                private_bit = mpkt.BSLBF(1)
                mpkt.seek(2)
                section_length_unused = mpkt.UIMSBF(2)
                section_length = mpkt.UIMSBF(10)
                section_boundary = mpkt.index() + section_length * 8
                t.add_row(['ID', table_id])
                t.add_row(['Section Syntax Indicator', section_syntax_indicator])
                t.add_row(['Section Length', section_length])
                print(t)


                # table syntax section
                program_number = mpkt.UIMSBF(16)
                mpkt.seek(2)
                version_number = mpkt.UIMSBF(5)
                current_next_indicator = mpkt.BSLBF(1)
                section_number = mpkt.UIMSBF(8)
                last_section_number = mpkt.UIMSBF(8)
                print(f'{section_number} : {last_section_number}')
                mpkt.seek(3)

                # PMT data
                PCR_PID = mpkt.UIMSBF(13)
                mpkt.seek(4)
                program_info_length_unused = mpkt.UIMSBF(2)
                program_info_lenght = mpkt.UIMSBF(10)
                print(f'prog info len: {program_info_lenght}')
                pil_boundary = mpkt.index() + program_info_lenght * 8
                # Elementary stream data
                while mpkt.index() < pil_boundary:
                    descriptor_tag = mpkt.UIMSBF(8)
                    print('descriptor tag : {}'.format(descriptor_tag))
                    descriptor_length = mpkt.UIMSBF(8)
                    print(descriptor_length)
                    descriptor_data = mpkt.BYTES(descriptor_length * 8)
                    print('descriptor_tag: {} descriptor_length: {} descriptor_data: {}'.format(
                        descriptor_tag, descriptor_length, descriptor_data))
                while mpkt.index() < section_boundary:
                    stream_type = mpkt.UIMSBF(8)
                    mpkt.seek(3)
                    elementary_pid = mpkt.UIMSBF(13)
                    mpkt.seek(4)
                    es_info_length_unused = mpkt.UIMSBF(2)
                    es_info_length = mpkt.UIMSBF(10)
                    print('streamtype: {} elem_pid: {} es_info_len: {}'.format(
                        hex(stream_type), elementary_pid, es_info_length))
                    es_info_boundary = (mpkt.index() + es_info_length * 8)
                    while mpkt.index() < es_info_boundary:
                        if elementary_pid == 2004 and stream_type == 0x0B: # DSMCC
                            # association tag descriptor [ETSI TR 101 202] [ISO/IEC 13818-6 [4]]
                            descriptor_tag = mpkt.UIMSBF(8)
                            descriptor_length = mpkt.UIMSBF(8)
                            desc_boundery = mpkt.index()  + descriptor_length * 8
                            Association_tag = mpkt.UIMSBF(16)
                            use = mpkt.UIMSBF(16)
                            print(f'use: {hex(use)}')
                            
                            print('descriptor tag: {}\tassociation tag: {}\n'.format(
                                hex(descriptor_tag), hex(Association_tag)
                            ))
                            if use == 0x0000: # DSI message (IOR of SG)  PID
                                selector_length = mpkt.UIMSBF(8)
                                transaction_id = mpkt.UIMSBF(32)
                                timeout = mpkt.UIMSBF(32)
                                print('Transaction id: {}\ttimeout: {} selector length: {}\n'.format(
                                    hex(transaction_id), hex(timeout), hex(selector_length)
                                ))
                            elif use == 0x0001:
                                selector_length = mpkt.UIMSBF(8)
                            else:
                                selector_length = mpkt.UIMSBF(8)
                                print(section_length)
                                tag_boundary =(mpkt.index() + selector_length * 8) 
                                while mpkt.index() < tag_boundary:
                                    carousel_type_id = mpkt.BSLBF(2)
                                    print(f'carousel_type_id {carousel_type_id}')
                                    mpkt.seek(6)
                                    transaction_id = mpkt.UIMSBF(32)
                                    time_out_value_DSI = mpkt.UIMSBF(32)
                                    time_out_value_DII = mpkt.UIMSBF(32)
                                    mpkt.seek(2)
                                    leak_rate = mpkt.BSLBF(22)
                            #last_bytes = desc_boundery - mpkt.index()
                            print(f'boundary: {desc_boundery}')
                            print(f'current pkt index: {mpkt.index()}')
                            while mpkt.index() < desc_boundery:
                                print(f'private: {mpkt.UIMSBF(8)}')

                            # stream identifier descriptor [EN 300 468 [1]]
                            descriptor_tag = mpkt.UIMSBF(8)
                            descriptor_length = mpkt.UIMSBF(8)
                            component_tag = mpkt.UIMSBF(8)
                            print(f'Component Tag: {hex(component_tag)}')

                            # carousel identifier descriptor  [ETSI TS 102 809]
                            descriptor_tag = mpkt.UIMSBF(8)
                            descriptor_length = mpkt.UIMSBF(8)
                            carousel_id = mpkt.UIMSBF(32)
                            format_id = mpkt.UIMSBF(8)
                            cid_boundary = mpkt.index() + descriptor_length * 8
                            print(f'pkt pos: {mpkt.index()}')
                            print(f'carousel ID: {hex(carousel_id)}, foramt: {hex(format_id)} cid_boundary: {cid_boundary}')
                            if format_id == 0x00:
                                while mpkt.index() < cid_boundary:
                                    print(f'private_data: {mpkt.UIMSBF(8)}') # private data
                            if format_id == 0x01:
                                module_version = mpkt.UIMSBF(8)
                                module_id = mpkt.UIMSBF(16)
                                blocksize = mpkt.UIMSBF(16)
                                modulesize = mpkt.UIMSBF(32)
                                compression_meth = mpkt.UIMSBF(8)
                                original_size = mpkt.UIMSBF(32)
                                print('blocksize:{}\tmodulesize: {}\tcompression: {}\torgsizse: {}\n'.format(
                                    blocksize, modulesize,compression_meth,original_size
                                ))
                                timeout = mpkt.UIMSBF(8)
                                objkeylen = mpkt.UIMSBF(8)
                                obj_bounary = mpkt.index() + objkeylen * 8
                                while mpkt.index() < obj_bounary:
                                    print(mpkt.BSLBF(8))
                                while mpkt.index() < (cid_boundary - obj_bounary - 21):
                                    print(mpkt.UIMSBF(8))
                            
                            # data component descriptor [ARIB STD - B10 Part2]
                            descriptor_tag = mpkt.UIMSBF(8)
                            descriptor_length = mpkt.UIMSBF(8)
                            data_componemt_id = mpkt.UIMSBF(16)
                            print(f'data component id: {hex(data_componemt_id)}')
                            dcd_boundary = mpkt.index() + descriptor_length * 8
                            print(descriptor_length)
                            while mpkt.index() < dcd_boundary:
                                # additional_data_component for data component descriptor [ARIB STD-B24]
                                mpkt.seek(2)
                                transmission_format = mpkt.UIMSBF(2)
                                document_resolution = mpkt.UIMSBF(3)
                                mpkt.seek(1)
                                organization_id = mpkt.UIMSBF(32)
                                application_id = mpkt.UIMSBF(16)
                                print(hex(application_id))
                                mpkt.seek(24)
                                carousel_id = mpkt.UIMSBF(8)
                                print(mpkt.BYTES(40))
                            
                        elif stream_type == 5 and elementary_pid == 2001:
                            # data component descriptor [ARIB STD - B10 Part2]
                            descriptor_tag = mpkt.UIMSBF(8)
                            dc_descriptor_length = mpkt.UIMSBF(8)
                            data_componemt_id = mpkt.UIMSBF(16)
                            print(f'dci {hex(data_componemt_id)} dc_desc_len: {dc_descriptor_length}')
                            ait_desc_boundary = (mpkt.index() + dc_descriptor_length * 8 )
                            while mpkt.index() < ait_desc_boundary:
                                # ait adentifier info [ARIB STD-B24]
                                application_type = mpkt.UIMSBF(16)
                                print((application_type))
                                transport_type = mpkt.BSLBF(1)
                                application_priority = mpkt.BSLBF(2)
                                AIT_version_number = mpkt.UIMSBF(5)
                                print(f'AIT VER: {AIT_version_number} application_type: {application_type}')

                                # application signaling descriptor [ETSI TS 102 809]
                                descriptor_tag = mpkt.UIMSBF(8)
                                asd_descriptor_length = mpkt.UIMSBF(8)
                                print(f'tag: {hex(descriptor_tag)} descrip length: {asd_descriptor_length}')
                                asd_boundary = (mpkt.index() + asd_descriptor_length * 8)
                                while mpkt.index() < asd_boundary:
                                    print(f'index; {mpkt.index()} < {asd_boundary}')
                                    mpkt.seek(1)
                                    application_type = mpkt.UIMSBF(15)
                                    mpkt.seek(3)
                                    AIT_version_number = mpkt.UIMSBF(5)
                                    print(f'AIT VER: {AIT_version_number} application_type: {application_type}')

                # end of Program Specific Information (PSI)

                crc32 = mpkt.UIMSBF(32)
                print(hex(crc32))

                #print(f'table_id: {table_id}\tsection_syntax_indicator: {section_syntax_indicator}\
                #    \tSL: {section_length}\tProgram #: {program_number}\tversion_number: {version_number}\tCurNextIndi: \
                #{current_next_indicator}\tSection #: {hex(section_number)}\tlast_section_#: {last_section_number}\tPIL: \
                #{hex(program_info_lenght)}')

                #sys.exit()

        if mpkt.packet_pid == 0x00: # PAT

            if mpkt.has_adaptation_field():
                print("FUCK~~")
                mpkt.parse_adaptation_fields() 

            if mpkt.has_payload():
                if mpkt.payload_unit_start_indicator == 1:
                    strp = mpkt.UIMSBF(8)
                    print(strp)
                    mpkt.seek(strp)
                    table_id = mpkt.UIMSBF(8)
                    section_syntax_indicator = mpkt.BSLBF(1)
                    mpkt.seek(3)
                    section_length = mpkt.UIMSBF(12)
                    boundary = mpkt.index() + section_length * 8 - 32
                    transport_stream_id = mpkt.UIMSBF(16)
                    mpkt.seek(2)
                    version_number = mpkt.UIMSBF(5)
                    current_nex_indicator = mpkt.BSLBF(1)
                    section_number = mpkt.UIMSBF(8)
                    last_section_number = mpkt.UIMSBF(8)
                    print(len(mpkt))
                    print(mpkt.index())
                    print(section_length * 8)

                    '''
                        gtables.py
                        tvd_service_id_sd = 0xe760 == 59232
                        tvd_pmt_pid_sd = 1031
                    '''
                    while mpkt.index() < boundary:
                        program_number = mpkt.UIMSBF(16)
                        print("Prog Number: ", program_number)
                        mpkt.seek(3)
                        if program_number == 0:
                            network_PID = mpkt.UIMSBF(13)
                            print("Network PID: ", network_PID)

                        else:
                            program_map_PID = mpkt.UIMSBF(13)
                            print("Program map PID: ", program_map_PID)
                        

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