import os
from csv import reader
from csv import writer

from util import CommandNames
from util import DEFAULT_ENGINE_DISPLACEMENT
from util import DEFAULT_VOLUMETRIC_EFFICIENCY
from util import FuelTypes
from util import Headers
from util import OBDModes
from util import calculate_fuel_consumption
from util import calculate_maf


def load_csv_file(input_path, delimiter=','):
    """ Loads a csv file into a matrix

    Parameters
    ----------
    input_path : str
        The path of the CSV file in string format

    delimiter : str , optional
        The separating string in the CSV file (the default is a comma)

    Returns
    -------
    list[list[str]]
        contains all the CSV data, separated into lines and by the delimiter

    """
    with open(input_path, "r") as f:
        matrix = []
        csv_reader = reader(f, delimiter=delimiter)
        for row in csv_reader:
            matrix.append(row)
        return matrix


def load_gps_file(input_path, delimiter=','):
    """ Loads a gps csv file into a matrix

    Parameters
    ----------
    input_path : str
        The path of the CSV file in string format
    delimiter : str , optional
        The separating string in the CSV file (the default is a comma)

    Returns
    -------
    List[List[Union[int, float]]]
        A matrix which contains all the CSV data, separated into lines and by the delimiter and converted to the correct types
    """
    return_matrix = []
    matrix = load_csv_file(input_path, delimiter)
    for row in matrix:
        return_matrix.append([int(row[0]), float(row[1]), float(row[2])])
    return return_matrix


def load_obd_file(input_path, delimiter=','):
    """Loads an obd csv file into a matrix

    Parameters
    ----------
    input_path : str
            The path of the CSV file in string format

    delimiter : str , optional
        The separating string in the CSV file (the default is a comma)

    Returns
    -------
    List[List[Union[int, str, float]]]
        A matrix which contains all the CSV data, separated into lines and by the delimiter and converted to the correct
        types
    """
    return_matrix = []
    matrix = load_csv_file(input_path, delimiter)
    for row in matrix:
        # Check which call it is for correct conversion
        if row[1] == CommandNames.SPEED.value or \
                row[1] == CommandNames.ENGINE_RPM.value or \
                row[1] == CommandNames.INTAKE_MANIFOLD_PRESSURE.value:
            return_matrix.append([int(row[0]), row[1], int(row[2])])  # int conversion
        elif row[1] == CommandNames.AIR_INTAKE_TEMP.value or \
                row[1] == CommandNames.MAF.value or \
                row[1] == CommandNames.FUEL_CONSUMPTION_RATE.value:
            return_matrix.append([int(row[0]), row[1], float(row[2])])  # float conversion
        else:
            return_matrix.append([int(row[0]), row[1], row[2]])  # no conversion
    return return_matrix


def load_drive_file(input_path, delimiter=',', has_header=True, obd_mode=OBDModes.MAF.value):
    # TODO need to write a strong loading function that understands the obd mode from the header, if there are no
    #   headers it will use the obd mode provided
    return_matrix = []
    with open(input_path, 'r') as file:
        csv_reader = reader(file, delimiter=delimiter)
        if has_header:
            next(csv_reader, None)
        for row in csv_reader:
            return_matrix.append(row)
    return return_matrix


def load_dir_gps_points(input_dir_path, has_header=True):
    """ Loads the gps points from all the files in a directory. All the files have to be either gps or drive files

    Parameters
    ----------
    input_dir_path : str
            The path of the CSV directory in string format

    has_header : bool , optional
        Does the files in the directory have headers (the default is True)

    Returns
    -------
    List[(float,float)]
        A list of tuples representing the GPS points


    See Also
    -------
    `load_file_gps_points()` which loads a single file
    """
    final_list = []
    for filename in os.listdir(input_dir_path):
        final_list.extend(load_file_gps_points(os.path.join(input_dir_path, filename), has_header=has_header))
    return final_list


def load_file_gps_points(input_path, has_header=True):
    """ Loads the gps points from either a gps or drive file

    Parameters
    ----------
    input_path : str
            The path of the CSV file in string format

    has_header : bool , optional
        Does the files in the folder have headers (the default is True)

    Returns
    -------
    List[(float,float)]
        A list of tuples representing the GPS points
    """
    with open(input_path, 'r') as file:
        csv_reader = reader(file)
        if has_header:
            next(csv_reader, None)
        return_list = [(float(row[1]), float(row[2])) for row in csv_reader]
    return return_list


def combine_drive_files(gps_input_path, obd_input_path, obd_mode, delimiter=',', fuel_type=FuelTypes.GASOLINE.value):
    """ Combines a pair of obd and gps files into a drive file

    Parameters
    ----------
    gps_input_path : str
        The path of the gps CSV file in string format
    obd_input_path : str
        The path of the obd CSV file in string format
    obd_mode : OBDModes enum value
        Which OBD is the vehicle in
    delimiter : str, optional
        The separating string in the CSV file (the default is a comma)
    fuel_type : FuelTypes enum value
        The fuel type used by the vehicle (the default is Gasoline)

    Returns
    -------
    List[List[Union[int,float]]]
        A drive matrix, containing the combined information from the GPS and OBD files which was converted to the
        correct types

    See Also
    -------
    `load_gps_file()` which loads a GPS file

    `load_obd_file()` which loads an OBD file
    """
    gps_matrix = load_gps_file(gps_input_path, delimiter=delimiter)
    obd_matrix = load_obd_file(obd_input_path, delimiter=delimiter)
    return_matrix = []
    for row in gps_matrix:
        return_matrix.append(__generate_full_data_call(row, obd_matrix, obd_mode=obd_mode, fuel_type=fuel_type))
    return return_matrix


def combine_drive_files_and_save(gps_input_path, obd_input_path, obd_mode, output_path, delimiter=',',
                                 fuel_type=FuelTypes.GASOLINE.value, create=True):
    """ Combines a pair of obd and gps files into a drive file

    Parameters
    ----------
     gps_input_path : str
        The path of the GPS CSV file in string format
    obd_input_path : str
        The path of the OBD CSV file in string format
    obd_mode : OBDModes enum value
        Which OBD is the vehicle in
    output_path : str
        The path of the output file in string format
    delimiter : str, optional
        The separating string in the CSV file (the default is a comma)
    fuel_type : FuelTypes enum value
        The fuel type used by the vehicle (the default is Gasoline)
    create : bool
        Create the output file if it does not exist (the default is True)

    Returns
    -------
    List[List[Union[int,float]]]
        A drive matrix, containing the combined information from the GPS and OBD files which was converted to the
        correct types

    See Also
    -------
    `load_gps_file()` which loads a gps file

    `load_obd_file()` which loads an obd file
    """
    matrix = combine_drive_files(gps_input_path, obd_input_path, obd_mode, delimiter=delimiter, fuel_type=fuel_type)
    with open(output_path, 'w+' if create else 'w', newline='') as file:
        csv_writer = writer(file, delimiter=delimiter)
        csv_writer.writerow(Headers[obd_mode])
        csv_writer.writerows(matrix)
    return matrix


def combine_dir_drive_files_and_save(input_dir_path, output_dir_path, obd_mode, delimiter=',',
                                     fuel_type=FuelTypes.GASOLINE.value, create=True, print_logs=True):
    """ Combines a pairs of obd and gps files in a directory into drive files and saves them

        Parameters
        ----------
         input_dir_path : str
            The path of the directory which holds the GPS and OBD CSV files
        output_dir_path : str
            The path for the output directory
        obd_mode : OBDModes enum value
            Which OBD mode is the vehicle in
        delimiter : str, optional
            The separating string in the CSV file (the default is a comma)
        fuel_type : FuelTypes enum value
            The fuel type used by the vehicle (the default is gasoline)
        create : bool
            Create the output file if it does not exist (the default is True)
        print_logs : bool
            Print logs while the function is running (the default is True)

        Returns
        -------
        List[List[Union[int,float]]]
            A drive matrix, containing the combined information from the GPS and OBD files which was converted to the
            correct types

        See Also
        -------
        `combine_drive_files_and_save()` for the single file version
        """
    gps_files = []
    obd_files = []
    output_files = []
    # Load the file paths into lists and generate the output_files list
    for filename in os.listdir(input_dir_path):
        if filename.endswith('.csv'):
            if 'GPS' in filename:
                gps_files.append(os.path.join(input_dir_path, filename))
                output_files.append(os.path.join(output_dir_path, filename.replace('GPS ', '')))
            elif 'OBD' in filename:
                obd_files.append(os.path.join(input_dir_path, filename))
    # Sort them so now all three would be aligned with one another
    sorted(gps_files)
    sorted(obd_files)
    sorted(output_files)
    if not os.path.exists(output_dir_path) and create:
        os.makedirs(output_dir_path)
    for i in range(len(gps_files)):
        if print_logs:
            print('started Working on ' + str(output_files[i]) + ',' + str(len(gps_files) - i) + ' are left')
        combine_drive_files_and_save(gps_files[i], obd_files[i], obd_mode, output_files[i], delimiter=delimiter,
                                     fuel_type=fuel_type)


def __generate_full_data_call(gps_call, obd_matrix, obd_mode=OBDModes.MAF.value, fuel_type=FuelTypes.GASOLINE.value,
                              volumetric_efficiency=DEFAULT_VOLUMETRIC_EFFICIENCY,
                              engine_displacement=DEFAULT_ENGINE_DISPLACEMENT):
    """Generates a full data row for the drive matrix depending on the `obd_mode`

    Parameters
    ----------
    gps_call : List(Union[int,float])
        A row from a GPS matrix
    obd_matrix : List(List(Union[int,str,float]))
        The OBD matrix
    obd_mode : OBDModes enum value
        Which OBD mode is the vehicle in (The default is MAF)
    fuel_type : FuelTypes enum value
        The fuel type used by the vehicle (the default is gasoline). Needed is `obd_mode` is not FUEL
    volumetric_efficiency : int
        Relates to the actual and theoretical volumetric flow rate in % (The default is from util module).
        Needed is `obd_mode` is RPM
    engine_displacement : int
        Volume of an engine's cylinders in cm^3 (The default is from util module). Needed is `obd_mode` is RPM

    Returns
    ----------
    List(List(Union[int,str,float]))
        A full data call, compromised of time, latlong, speed, fuel flow. Depending on `obd_mode` it might also include
        more information

    See Also
    --------
    `__generate_full_rpm_data_call()` for the RPM data call creation

    `__generate_full_maf_data_call()` for the MAF data call creation

    `__generate_full_fuel_data_call()` for the FUEL data call creation
    """
    data_call = [gps_call[0], gps_call[1], gps_call[2]]
    if obd_mode == OBDModes.RPM.value:
        data_call.extend(__generate_full_rpm_data_call(gps_call, obd_matrix, fuel_type=fuel_type,
                                                       volumetric_efficiency=volumetric_efficiency,
                                                       engine_displacement=engine_displacement))
    elif obd_mode == OBDModes.MAF.value:
        data_call.extend(__generate_full_maf_data_call(gps_call, obd_matrix, fuel_type=fuel_type))
    else:
        data_call.extend(__generate_full_fuel_data_call(gps_call, obd_matrix))
    return data_call


def load_tuples_csv_file(input_path):
    with open(os.path.join(input_path), 'r') as file:
        csv_reader = reader(file)
        return_list = [(float(row[0]), float(row[1])) for row in csv_reader]
    return return_list


def __generate_full_rpm_data_call(gps_call, obd_matrix, fuel_type=FuelTypes.GASOLINE.value,
                                  volumetric_efficiency=DEFAULT_VOLUMETRIC_EFFICIENCY,
                                  engine_displacement=DEFAULT_ENGINE_DISPLACEMENT):
    """Generates a full data row for the drive matrix depending on the `obd_mode`

    Parameters
    ----------
    gps_call : List(Union[int,float])
        A row from a GPS matrix
    obd_matrix : List(List(Union[int,str,float]))
        The OBD matrix
    fuel_type : FuelTypes enum value
        The fuel type used by the vehicle (the default is gasoline)
    volumetric_efficiency : int
                Relates to the actual and theoretical volumetric flow rate in % (The default is from util module)
    engine_displacement : int
        Volume of an engine's cylinders in cm^3 (The default is from util module)

    Returns
    ----------
    List(List(Union[int,str,float]))
        A full data call, compromised of time, latlong, speed, and obd information

    Notes
    --------
    The runtime of this function can be vastly improved if the search for the closest obd call would be a binary
    search instead of linear search
    """
    rpm_value = 0
    rpm_time_diff = -1
    map_value = 0
    map_time_diff = -1
    iat_value = 0.0
    iat_time_diff = -1
    speed_value = 0
    speed_time_diff = -1
    # Find the closest OBD calls to the time of the GPS call
    for obd_call in obd_matrix:
        if obd_call[1] == CommandNames.ENGINE_RPM.value:
            if rpm_time_diff == -1 or abs(obd_call[0] - gps_call[0]) < rpm_time_diff:
                rpm_time_diff = abs(obd_call[0] - gps_call[0])
                rpm_value = obd_call[2]
        elif obd_call[1] == CommandNames.INTAKE_MANIFOLD_PRESSURE.value:
            if map_time_diff == -1 or abs(obd_call[0] - gps_call[0]) < rpm_time_diff:
                map_time_diff = abs(obd_call[0] - gps_call[0])
                map_value = obd_call[2]
        elif obd_call[1] == CommandNames.AIR_INTAKE_TEMP.value:
            if iat_time_diff == -1 or abs(obd_call[0] - gps_call[0]) < rpm_time_diff:
                iat_time_diff = abs(obd_call[0] - gps_call[0])
                iat_value = obd_call[2]
        else:
            if speed_time_diff == -1 or abs(obd_call[0] - gps_call[0]) < rpm_time_diff:
                speed_time_diff = abs(obd_call[0] - gps_call[0])
                speed_value = obd_call[2]
    maf_value = calculate_maf(rpm_value, map_value, iat_value, volumetric_efficiency=volumetric_efficiency,
                              engine_displacement=engine_displacement)
    fuel_value = calculate_fuel_consumption(maf_value, fuel_type=fuel_type)
    return [speed_value, rpm_value, map_value, iat_value, maf_value, fuel_value]


def __generate_full_maf_data_call(gps_call, obd_matrix, fuel_type=FuelTypes.GASOLINE.value):
    """Generates a full data row for the drive matrix depending on the `obd_mode`

    Parameters
    ----------
    gps_call : List(Union[int,float])
        A row from a GPS matrix
    obd_matrix : List(List(Union[int,str,float]))
        The OBD matrix
    fuel_type : FuelTypes enum value
        The fuel type used by the vehicle (the default is gasoline)

    Returns
    ----------
    List(List(Union[int,str,float]))
        A full data call, compromised of time, latlong, speed, and OBD information

    Notes
    --------
    The runtime of this function can be vastly improved if the search for the closest obd call would be a binary
    search instead of linear search
    """
    maf_value = 0.0
    maf_time_diff = -1
    speed_value = 0
    speed_time_diff = -1
    # Find the closest OBD calls to the time of the GPS call
    for obd_call in obd_matrix:
        if obd_call[1] == CommandNames.MAF.value:
            if maf_time_diff == -1 or abs(obd_call[0] - gps_call[0]) < maf_time_diff:
                maf_time_diff = abs(obd_call[0] - gps_call[0])
                maf_value = obd_call[2]
        else:
            if speed_time_diff == -1 or abs(obd_call[0] - gps_call[0]) < speed_time_diff:
                speed_time_diff = abs(obd_call[0] - gps_call[0])
                speed_value = obd_call[2]
    return [speed_value, maf_value, calculate_fuel_consumption(maf_value, fuel_type=fuel_type)]


def __generate_full_fuel_data_call(gps_call, obd_matrix):
    """Generates a full data row for the drive matrix depending on the `obd_mode`

    Parameters
    ----------
    gps_call : List(Union[int,float])
        A row from a GPS matrix
    obd_matrix : List(List(Union[int,str,float]))
        The OBD matrix

    Returns
    ----------
    List(List(Union[int,str,float]))
        A full data call, compromised of time, latlong, speed, and the fuel flow

    Notes
    --------
    The runtime of this function can be vastly improved if the search for the closest obd call would be a binary
    search instead of linear search
    """
    fuel_consumption_value = 0.0
    fuel_consumption_time_diff = -1
    speed_value = 0
    speed_time_diff = -1
    # Find the closest OBD calls to the time of the GPS call
    for obd_call in obd_matrix:
        if obd_call[1] == CommandNames.FUEL_CONSUMPTION_RATE.value:
            if fuel_consumption_time_diff == -1 or abs(obd_call[0] - gps_call[0]) < fuel_consumption_time_diff:
                fuel_consumption_time_diff = abs(obd_call[0] - gps_call[0])
                fuel_consumption_value = obd_call[2]
        else:
            if speed_time_diff == -1 or abs(obd_call[0] - gps_call[0]) < speed_time_diff:
                speed_time_diff = abs(obd_call[0] - gps_call[0])
                speed_value = obd_call[2]
    return [speed_value, fuel_consumption_value]


def save_tuples_to_csv(tuple_list, output_path, create=True):
    with open(output_path, 'w+' if create else 'w') as file:
        for point in tuple_list:
            file.write(str(point[0]) + ',' + str(point[1]) + '\n')
