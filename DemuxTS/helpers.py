from bitstring import ConstBitStream

def bitwise_and_bytes(header_bytes, bitmask):
    result_int = int.from_bytes(header_bytes, byteorder="big") & bitmask
    result_byte =  result_int.to_bytes(len(header_bytes),byteorder="big")
    return int.from_bytes(result_byte, byteorder='big')

def bytes_to_int(binary_data):
    return int.from_bytes(binary_data, big)

if __name__ == "__main__":
    pass