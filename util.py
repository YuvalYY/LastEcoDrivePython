from enum import Enum

from geopy import distance


class OBDModes(Enum):
    RPM = 1  # Engine RPM, intake manifold pressure, and air intake temperature readings
    MAF = 2  # Mass air flow readings
    FUEL = 3  # Fuel consumption readings


class CommandNames(Enum):
    SPEED = "Vehicle Speed"
    AIR_INTAKE_TEMP = 'Air Intake Temperature'
    ENGINE_RPM = 'Engine RPM'
    INTAKE_MANIFOLD_PRESSURE = "Intake Manifold Pressure"
    MAF = "Mass Air Flow"
    FUEL_CONSUMPTION_RATE = 'Fuel Consumption Rate'


class FuelTypes(Enum):  # grams of air to 1 gram of fuel, g/dm^3
    GASOLINE = 14.7, 820
    DIESEL = 14.5, 750


Headers = {
    1: ['Time', 'Latitude', 'Longitude', 'Speed', 'Engine RPM', 'Intake Manifold Pressure',
        'Air Intake Temperature', 'Mass Air Flow', 'Fuel Consumption Rate'],
    2: ['Time', 'Latitude', 'Longitude', 'Speed', 'Mass Air Flow', 'Fuel Consumption Rate'],
    3: ['Time', 'Latitude', 'Longitude', 'Speed', 'Fuel Consumption Rate']

}

R = 8.314  # J/K/mole
MMAir = 28.97  # kgair/kmolair
MILLIS_IN_HOUR = 3600000

DEFAULT_VOLUMETRIC_EFFICIENCY = 80  # percent
DEFAULT_ENGINE_DISPLACEMENT = 1999  # cm^3

FROM_HOME_START_TUPLE = (31.777961976722185, 34.66809331296997)
FROM_HOME_END_TUPLE = (31.96329274784879, 34.75862040227392)
TO_HOME_START_TUPLE = (31.964473041755, 34.757973118655065)
TO_HOME_END_TUPLE = (31.777838011240725, 34.66753131449542)


def calculate_maf(rpm, map1, iat, volumetric_efficiency=DEFAULT_VOLUMETRIC_EFFICIENCY,
                  engine_displacement=DEFAULT_ENGINE_DISPLACEMENT):
    """Mass air flow calculation

    Parameters
    ----------
    rpm : int
        Engine RPM (OBD2 PID 010C0) in RPM
    map1 : int
        Manifold absolute pressure (OBD2 PID 010B) in kPa
    iat : float
        Intake air temperature (OBD2 PID 010F) in celsius
    volumetric_efficiency : int
        Relates to the actual and theoretical volumetric flow rate in %
    engine_displacement : int
        Volume of an engine's cylinders in cm^3

    Returns
    ----------
    float
        Mass air flow in g/s

    See Also
    --------
    "Assessing the impact of driving behavior on instantaneous fuel consumption" from which the formula is taken

    `calculate_fuel_consumption()` for a fuel flow calculation

    """
    iat = iat + 273.15  # converting celsius to kelvin
    imap = rpm * map1 / iat / 2  # synthetic variable
    return ((imap / 60) * (volumetric_efficiency / 100) * engine_displacement * (MMAir / R)) / 1000


def calculate_fuel_consumption(maf, fuel_type=FuelTypes.GASOLINE.value):
    """mass air flow calculation

    Parameters
    ----------
    maf : float
        Mass air flow (OBD2 PID 0110) in g/s
    fuel_type : FuelTypes enum value
        The fuel type used by the vehicle (the default is Gasoline)

    Returns
    ----------
    float
        fuel flow in l/h

    See Also
    --------
    "Assessing the impact of driving behavior on instantaneous fuel consumption" from which the formula is taken

    `calculate_maf()` for a mass air flow calculation
    """
    return (maf * 3600) / (fuel_type[0] * fuel_type[1])


def calculate_cost(time1, time2, fcr1, fcr2):
    time_in_hours = abs(time1 - time2) / MILLIS_IN_HOUR
    high = max(fcr1, fcr2)
    low = min(fcr1, fcr2)
    return low * time_in_hours + ((high - low) * time_in_hours) / 2


def calculate_route_length(gps_tuple_list):
    sum1 = 0
    for i in range(len(gps_tuple_list) - 1):
        sum1 += distance.distance(gps_tuple_list[i], gps_tuple_list[i + 1]).km
    return sum1


def get_drive_between_two_points(drive_matrix, start, end):
    start_position = 0
    closest_start = (float(drive_matrix[0][1]), float(drive_matrix[0][2]))
    end_position = 0
    closest_end = (float(drive_matrix[0][1]), float(drive_matrix[0][2]))
    for i in range(1, len(drive_matrix)):
        ctupple = (float(drive_matrix[i][1]), float(drive_matrix[i][2]))
        if distance.distance(start, closest_start).m > distance.distance(start, ctupple).m:
            start_position = i
            closest_start = ctupple
        if distance.distance(end, closest_end).m > distance.distance(end, ctupple).m:
            end_position = i
            closest_end = ctupple
    return drive_matrix[start_position:end_position]


def find_closest_center(lat, lon, master_list):
    min_diff = -1
    result_lat = 0
    result_long = 0
    for point in master_list:
        if distance.distance(point, (lat, lon)).m < min_diff or min_diff == -1:
            min_diff = distance.distance(point, (lat, lon)).m
            result_lat = point[0]
            result_long = point[1]
    return result_lat, result_long


def calculate_csv_fuel_cost(input_path, has_headers=True):
    temp_matrix = []
    sum0 = 0
    with open(input_path, 'r') as file:
        if has_headers:
            next(file, None)
        for line in file:
            linesplit = line.split(',')
            temp_matrix.append([int(linesplit[0]), float(linesplit[-1])])
    for i in range(len(temp_matrix) - 1):
        sum0 += calculate_cost(temp_matrix[i][0], temp_matrix[i + 1][0], temp_matrix[i][1], temp_matrix[i + 1][1])
    return sum0
