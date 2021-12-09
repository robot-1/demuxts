from DemuxTS.printtable import printpsi

def pat_table(mpkt):

    if mpkt.has_adaptation_field():
        print("FUCK~~")
        mpkt.parse_adaptation_fields() 

    if mpkt.has_payload():
        if mpkt.payload_unit_start_indicator == 1:
            strp = mpkt.UIMSBF(8)
            #print(strp)
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
            #print(len(mpkt))
            #print(mpkt.index())
            #print(section_length * 8)

            '''
                gtables.py
                tvd_service_id_sd = 0xe760 == 59232
                tvd_pmt_pid_sd = 1031
            '''
            pp = printpsi.Printer( ['Program Number', 'Network PID', 'PMT ID'], title='Program Association Table')
            data = list()
            while mpkt.index() < boundary:
                program_map_PID = '-'
                network_PID = '-'
                program_number = mpkt.UIMSBF(16)
                mpkt.seek(3)
                if program_number == 0:
                    network_PID = mpkt.UIMSBF(13)

                else:
                    program_map_PID = mpkt.UIMSBF(13)
                try:
                    program_map_PID = int(program_map_PID)
                except:
                    pass
                data.append({'program number':hex(program_number), 'network PID': network_PID, 'PMT ID': program_map_PID})
            pp.print_table(data)