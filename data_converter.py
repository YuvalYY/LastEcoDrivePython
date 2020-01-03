from pyperclip import copy

from csv_util import load_drive_file
from util import OBDModes


def drive_csv_to_separate_coordinates(input_path, has_header=True, obd_mode=OBDModes.MAF.value, delimiter=',',
                                      copy_result=True, add_wrappers=True, add_speed=True):
    matrix = load_drive_file(input_path, has_header=has_header, delimiter=delimiter, obd_mode=obd_mode)
    string = ''
    if add_wrappers:
        string += '{"type": "FeatureCollection","features": [\n'
    for row in matrix:
        string += '{"type": "Feature","properties": {'
        if add_speed:
            string += '"Speed":' + str(row[3])
        string += '},"geometry": {"type": "Point","coordinates": ['
        string += str(row[2]) + "," + str(row[1])  # Lat and long are reversed in the program for some reason
        string += ']}},\n'
    string = string[:-2]
    if add_wrappers:
        string += '\n]}'
    if copy_result:
        copy(string)
    return string
