from bitstring import ConstBitStream
from prettytable import PrettyTable
from collections import ChainMap
import logging
logger = logging.getLogger(__name__)
section = []


def pmt_table(mpkt):
    #print(f"Packet[{pkts_cnt}] SYNC: {hex(mpkt.sync_byte)}\tTEI: {mpkt.transport_error_indicator} \
    #\tPUSI: {mpkt.payload_unit_start_indicator}\tTP: {mpkt.transport_priority}\tPID: {mpkt.packet_pid} \
    #\tAFC: {mpkt.adaptation_field_control}\tCONT. CNT : {int(mpkt.continuity_counter,2)}")
    psi_fields = dict()
    t = PrettyTable( ['Fields', 'Value'], title='PMT HEADER')
    if mpkt.has_adaptation_field():
        mpkt.parse_adaptation_fields() 

    if mpkt.has_payload():
        if mpkt.payload_unit_start_indicator == 1:
            strp = mpkt.UIMSBF(8)
            print(f'data pointer {strp}')
            if len(section) == 0:
                pass
        # start of Program Specificic Information (PSI)
        # table header
        table_id = mpkt.UIMSBF(8) # always 0x02 for PMT, might not exist !
        section_syntax_indicator = mpkt.BSLBF(1) # must be 1
        private_bit = mpkt.BSLBF(1)
        mpkt.seek(2)
        section_length_unused = mpkt.UIMSBF(2)
        section_length = mpkt.UIMSBF(10)
        section_boundary = mpkt.index() + section_length * 8
        psi_fields.update({
            'id' :table_id,
            'ssi' :section_syntax_indicator,
            'sec_lengh' : section_length
            })

        # table syntax section
        program_number = mpkt.UIMSBF(16)
        mpkt.seek(2)
        version_number = mpkt.UIMSBF(5)
        current_next_indicator = mpkt.BSLBF(1)
        section_number = mpkt.UIMSBF(8)
        last_section_number = mpkt.UIMSBF(8)
        psi_fields.update({
            'section num': section_number,
            'last section num': last_section_number
        })
        mpkt.seek(3)

        # PMT data
        PCR_PID = mpkt.UIMSBF(13)
        mpkt.seek(4)
        program_info_length_unused = mpkt.UIMSBF(2)
        program_info_lenght = mpkt.UIMSBF(10)
        pil_boundary = mpkt.index() + program_info_lenght * 8
        psi_fields.update({
            'program info len' :program_info_lenght
        })
        es_list = list()
        t2 = PrettyTable( ['stream type', 'elemetar pid'], title='PMT ES ID')
        # Elementary stream data
        while mpkt.index() < pil_boundary:
            es_datafields = dict()
            descriptor_tag = mpkt.UIMSBF(8)
            descriptor_length = mpkt.UIMSBF(8)
            descriptor_data = mpkt.BYTES(descriptor_length * 8)
            es_list.append(es_datafields.update({
                'descriptor tag' : descriptor_tag,
                'descriptor length': descriptor_length,
                'descriptor data': descriptor_data
            }))
        # start of ES INFO
        while mpkt.index() < section_boundary:
            stream_type = mpkt.UIMSBF(8)
            mpkt.seek(3)
            elementary_pid = mpkt.UIMSBF(13)
            mpkt.seek(4)
            es_info_length_unused = mpkt.UIMSBF(2)
            es_info_length = mpkt.UIMSBF(10)
            es_list.append({
                'stream type' : stream_type,
                'elementary pid' : elementary_pid,
                'es info lengh' : es_info_length
            })
            print(es_list)
            es_info_boundary = (mpkt.index() + es_info_length * 8)
            while mpkt.index() < es_info_boundary:
                if elementary_pid == 2004 and stream_type == 0x0B: # DSMCC
                    # association_tag_descriptor [ETSI TR 101 202] [ISO/IEC 13818-6 [4]]
                    descriptor_tag = mpkt.UIMSBF(8)
                    descriptor_length = mpkt.UIMSBF(8)
                    desc_boundery = mpkt.index()  + descriptor_length * 8
                    association_tag = mpkt.UIMSBF(16)
                    print(f'association tag: {hex(association_tag)}')
                    use = mpkt.UIMSBF(16)
                    print(f'use: {hex(use)}')
                    
                    if use == 0x0000: # DSI message (IOR of SG)  PID
                        selector_length = mpkt.UIMSBF(8)
                        print(f'Selector length: {hex(selector_length)}')
                        transaction_id = mpkt.UIMSBF(32)
                        timeout = mpkt.UIMSBF(32)
                    elif use == 0x0001:
                        selector_length = mpkt.UIMSBF(8)
                    else:
                        selector_length = mpkt.UIMSBF(8)
                        tag_boundary =(mpkt.index() + selector_length * 8) 
                        while mpkt.index() < tag_boundary:
                            carousel_type_id = mpkt.BSLBF(2)
                            mpkt.seek(6)
                            transaction_id = mpkt.UIMSBF(32)
                            time_out_value_DSI = mpkt.UIMSBF(32)
                            time_out_value_DII = mpkt.UIMSBF(32)
                            mpkt.seek(2)
                            leak_rate = mpkt.BSLBF(22)
                    #last_bytes = desc_boundery - mpkt.index()
                    #print(mpkt.index() < desc_boundery)
                    #while mpkt.index() < desc_boundery:
                    #    mpkt.UIMSBF(8) # private data

                    #print(mpkt.index() < desc_boundery)

                    # stream identifier descriptor [EN 300 468 [1]]
                    descriptor_tag = mpkt.UIMSBF(8)
                    descriptor_length = mpkt.UIMSBF(8)
                    component_tag = mpkt.UIMSBF(8)
                    print(f'component tag: {hex(component_tag)}')
                    print(f'transaction id: {hex(transaction_id)}')
                    print(f'timeout: {hex(timeout)}')

                    # carousel identifier descriptor  [ETSI TS 102 809]
                    descriptor_tag = mpkt.UIMSBF(8)
                    descriptor_length = mpkt.UIMSBF(8)
                    print(f'cid_desc len: {hex(descriptor_length)}')
                    cid_boundary = mpkt.index() + descriptor_length * 8
                    carousel_id = mpkt.UIMSBF(32)
                    format_id = mpkt.UIMSBF(8) # this is zero (0), no format specifier
                    print(f'descriptor tag: {hex(descriptor_tag)}')
                    print(f'carousel id: {hex(carousel_id)}')
                    print(f'format id: {hex(format_id)}')
                    if format_id == 0x00:
                        while mpkt.index() < cid_boundary:
                            try:
                                mpkt.UIMSBF(8) # private data
                            except:
                                break
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
                    descriptor_tag = mpkt.UIMSBF(8) # 0xfd set by opencaster
                    descriptor_length = mpkt.UIMSBF(8)
                    dcd_boundary = mpkt.index() + descriptor_length * 8
                    data_componemt_id = mpkt.UIMSBF(16)
                    print(f'dcd tag: {hex(descriptor_tag)}')
                    print(f'data component id: {hex(data_componemt_id)}')
                    while mpkt.index() < dcd_boundary:
                        # additional_data_component(additional_ginga_j_info) 
                        # for data component descriptor [ARIB STD-B24], ABNT NBR 15606-3:2007
                        transmission_format = int(mpkt.BSLBF(2),2)
                        application_identifier_flag = int(mpkt.BSLBF(1),2)
                        document_resolution = int(mpkt.BSLBF(4),2)
                        independent_flag = mpkt.BSLBF(1)
                        if application_identifier_flag == 1:
                            #application identifier, ABNT NBR 15606-3:2007 page 39
                            organization_id = mpkt.UIMSBF(32)
                            application_id = mpkt.UIMSBF(16)
                        elif transmission_format == 0:
                            download_id = mpkt.UIMSBF(32)
                            ondemand_retrieval_flag = mpkt.BSLBF(1)
                            file_storable_flag = mpkt.BSLBF(1)
                            event_section_flag = mpkt.BSLBF(1)
                            reserved_future_use = mpkt.BSLBF(5)
                        elif transmission_format == 1:
                            reserved_future_use = mpkt.BSLBF(8)
                        elif transmission_format == 2:
                            carousel_id = mpkt.UIMSBF(32)
                            print(f'carousel id: {hex(carousel_id)}')
                            ondemand_retrieval_flag = mpkt.BSLBF(1)
                            file_storable_flag = mpkt.BSLBF(1)
                            event_section_flag = mpkt.BSLBF(1)
                            reserved_future_use = mpkt.BSLBF(5)
                        print(f'transmission format: {hex(transmission_format)}')
                        print(f'document resolution: {hex(document_resolution)}')
                        print(f'organization id: {hex(organization_id)}')
                        print(f'application id: {hex(application_id)}')
                    
                    
                    
                elif stream_type == 5 and elementary_pid == 2001:
                    # data component descriptor [ARIB STD - B10 Part2]
                    descriptor_tag = mpkt.UIMSBF(8)
                    dc_descriptor_length = mpkt.UIMSBF(8)
                    ait_desc_boundary = (mpkt.index() + dc_descriptor_length * 8 )
                    data_componemt_id = mpkt.UIMSBF(16) # this should be 0xA3
                    print(f'data comp id: {hex(data_componemt_id)}')
                    while mpkt.index() < ait_desc_boundary:
                        # ait adentifier info [ARIB STD-B24]
                        application_type = mpkt.UIMSBF(16) # this should be 9
                        transport_type = mpkt.BSLBF(1)
                        application_priority = mpkt.BSLBF(2)
                        AIT_version_number = mpkt.UIMSBF(5)

                        # application signaling descriptor [ETSI TS 102 809]
                        descriptor_tag = mpkt.UIMSBF(8)
                        asd_descriptor_length = mpkt.UIMSBF(8)
                        asd_boundary = (mpkt.index() + asd_descriptor_length * 8)
                        while mpkt.index() < asd_boundary:
                            mpkt.seek(1)
                            application_type = mpkt.UIMSBF(15)
                            mpkt.seek(3)
                            AIT_version_number = mpkt.UIMSBF(5)
             
        # end of ES INFO
            
        crc32 = mpkt.UIMSBF(32)
        print(f'CRC32 {hex(crc32)}')