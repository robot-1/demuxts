from multiprocessing import Pool
from prettytable import PrettyTable


class Printer(PrettyTable):
    def __init__(self, header, title):
        self.header_len = len(header)
        super(Printer, self).__init__(header, title=title)
    
    def add_data(self, data):
        self.add_row(data)

    def print_table(self, psi_table):
        if isinstance(psi_table, list):
            for item in psi_table:
                self.add_row(item.values())
        elif isinstance(psi_table, dict):
            items = psi_table.items()
            self.add_rows(items)
        else:
            raise ValueError('Must be of type list or dict')


        
        print(self.__str__())
