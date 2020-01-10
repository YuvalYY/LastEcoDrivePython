import csv
import os

from geopy import distance

from csv_util import load_drive_file
from csv_util import load_driving_model_file
from util import calculate_cost
from util import find_closest_center
from vertex import VertexFactory


def generate_drive_model(file_path, centers_list, model_save_path=None):
    """
    See Also
    ----------
    `csv_util.load_tuples_csv_file()` to load the tuple list.
    """
    matrix = __generate_matrix_for_processing(file_path, centers_list)
    found_first = False
    last_model = []
    sum1 = 0
    current = 0
    for i in range(len(matrix) - 1):
        if found_first:
            sum1 += calculate_cost(matrix[i][0], matrix[i - 1][0], matrix[i][4], matrix[i - 1][4])
            if matrix[i][-1]:
                last_model.append(
                    [matrix[i][5], matrix[i][6], matrix[i][3] // 5 * 5, 0])  # changed which latlon we take
                last_model[current][3] = sum1
                sum1 = 0
                current += 1
        else:
            if matrix[i][-1]:
                last_model.append([matrix[i][5], matrix[i][6], matrix[i][3] // 5 * 5, 0])
                found_first = True
    if model_save_path:
        with open(model_save_path, "w+", newline='') as f:
            writer = csv.writer(f)
            writer.writerows(last_model)
    return last_model


def __generate_matrix_for_processing(file_path, centers_list):
    matrix = [[int(row[0]), float(row[1]), float(row[2]), int(row[3]), float(row[-1]), None, None, False] for row in
              load_drive_file(file_path)]
    shortest_dist_dict = {x: -1 for x in centers_list}
    checked_dict = {x: False for x in centers_list}
    for row in matrix:
        row[5], row[6] = find_closest_center(row[1], row[2], centers_list)
        if shortest_dist_dict[(row[5], row[6])] == -1 or \
                distance.distance((row[1], row[2]), (row[5], row[6])) < shortest_dist_dict[(row[5], row[6])]:
            shortest_dist_dict[(row[5], row[6])] = distance.distance((row[1], row[2]), (row[5], row[6]))
    for row in matrix:
        if distance.distance((row[1], row[2]), (row[5], row[6])) == shortest_dist_dict[(row[5], row[6])] and \
                not checked_dict[(row[5], row[6])]:
            row[-1] = True
            checked_dict[(row[5], row[6])] = True
    return matrix


def cheapest_path_model(dir_path):  # change name to find cheapest path
    vertex_factory = VertexFactory()
    for filename in os.listdir(dir_path):
        __load_driving_model_file(os.path.join(dir_path, filename), vertex_factory)
    vertex_factory.calculate_edge_costs()

    # test printing, need to keep going
    # for v in vertex_factory.get_all_vertexes():
    #     if len(v.neighbors) > 3:
    #         print(v)
    #         v.print_neighbors()
    # TODO still needs to calculate the cheapest route
    visited_vertexes = []
    found_vertexes = [vertex_factory.get_end()]
    while found_vertexes:
        current_vertex = min(found_vertexes, key=lambda x: x.cost_to)
        visited_vertexes.append(current_vertex)
        found_vertexes.remove(current_vertex)
        for neighbor in current_vertex.get_neighbors():
            if neighbor not in visited_vertexes and neighbor not in found_vertexes:
                found_vertexes.append(neighbor)
        current_vertex.update_neighbors()

    # test section - still needs to return the model
    curr = vertex_factory.get_start()
    return_model = []
    while True:
        curr = vertex_factory.get_vertex_by_id(curr.father_id)
        return_model.append([curr.lat, curr.lon, curr.speed, curr.cost_to])
        if curr.father_id == '200,200,0':
            break
    return_model = list(reversed(return_model))

    for i in range(len(return_model) - 1):
        return_model[i][3] = return_model[i + 1][3] - return_model[i][3]
    return_model[-1][3] = 0

    for line in return_model:
        print(line)

    return return_model


def __load_driving_model_file(file_path, vertex_factory, connect_start=True, connect_end=True):
    # the function builds the graph in reverse, if in the real world we went from a to b, in the graph we would be able
    # to go from b to a and not from a to b
    drive_model = load_driving_model_file(file_path)
    if connect_start:
        vertex_factory.get_vertex(drive_model[0][0], drive_model[0][1], drive_model[0][2]).add_neighbor(
            vertex_factory.get_start(), 0)
    for i in range(len(drive_model) - 1, 0, -1):
        vertex_factory.get_vertex(drive_model[i][0], drive_model[i][1], drive_model[i][2] // 5 * 5).add_neighbor(
            vertex_factory.get_vertex(drive_model[i - 1][0], drive_model[i - 1][1], drive_model[i - 1][2] // 5 * 5),
            drive_model[i - 1][-1])
    if connect_end:
        vertex_factory.get_end().add_neighbor(
            vertex_factory.get_vertex(drive_model[-1][0], drive_model[-1][1], drive_model[-1][2]), 0)
