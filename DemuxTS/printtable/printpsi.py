
from prettytable import PrettyTable


class Printer(PrettyTable):
    def __init__(self):
        super(Printer, self).__init__(header, title)
    
    def add_data(self, data):
        self.add_row(data)

    def print_table(self, psi_table):
        print(psi_table)
