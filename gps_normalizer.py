import os
from random import sample

from geopy import distance

from csv_util import save_tuples_to_csv


def normalize(tuple_list, route_length, distance_between_points, iteration_count, print_logs=True,
              save=False, save_dir_path=''):
    centers_list = sample(set(tuple_list), int(route_length / distance_between_points))
    if save:
        save_tuples_to_csv(centers_list, os.path.join(save_dir_path, 'Initial Choice.csv'))
    for i in range(iteration_count):
        if print_logs:
            print('Iteration ' + str(i))
        centers_list = __iteration_with_all_points(tuple_list, centers_list, print_logs=print_logs)
        if save:
            save_tuples_to_csv(centers_list, os.path.join(save_dir_path, 'Iteration ' + str(i) + '.csv'))
    return centers_list


def __iteration_with_all_points(tuple_list, centers_list, print_logs=True):
    centers_dict = {center: [] for center in centers_list}
    length = len(tuple_list)
    for i in range(length):
        if print_logs:
            print(length - i)
        min_dist = distance.distance(tuple_list[i], centers_list[0])
        current_center = centers_list[0]
        for j in range(1, len(centers_list)):
            if distance.distance(tuple_list[i], centers_list[j]) < min_dist:
                min_dist = distance.distance(tuple_list[i], centers_list[j])
                current_center = centers_list[j]
        centers_dict[current_center].append(tuple_list[i])
    return_list = []
    for key in centers_dict:
        length = len(centers_dict[key])
        if length != 0:
            lat_sum = sum([x[0] for x in centers_dict[key]])
            lon_sum = sum([x[1] for x in centers_dict[key]])
            return_list.append((lat_sum / length, lon_sum / length))
    return return_list


def __iteration_with_splitting(tuple_route_list, centers_list, split_count, iteration_count, print_logs=True):
    all_sections = []
    for i in range(split_count):
        all_sections.append([])
    for route_list in tuple_route_list:
        temp = split_tuple_list(route_list, split_count)
        for i in range(split_count):
            all_sections[i].extend(temp[i])
    # create the initial center list
    # do the iterations
    # for each iteration run the algorithm for finding the sections' centers


def split_tuple_list(tuple_list, split_count):
    # The algorithm doesnt take the last point it checks, it checks if the i->i+1 would make it over 1km but doesn't
    # take it into the sub route
    sections_list = []
    current_position = 0
    current_split = 0
    sum1 = 0
    for i in range(len(tuple_list) - 1):  # change to 2 if you want to include it
        sum1 += distance.distance(tuple_list[i], tuple_list[i + 1]).km
        if sum1 > 1:
            sections_list.append(tuple_list[current_position:i + 1])  # change to 2 if you want to include it
            current_position = i
            current_split += 1
            sum1 = 0
            if current_split == split_count - 1:
                break
    sections_list.append(tuple_list[current_position:-1])
    return sections_list


def __split_iteration(tuple_list, centers_list, print_logs=True):
    centers_dict = {center: [] for center in centers_list}
    length = len(tuple_list)
    for i in range(length):
        if print_logs:
            print(length - i)
        min_dist = distance.distance(tuple_list[i], centers_list[0])
        current_center = centers_list[0]
        for j in range(1, len(centers_list)):
            if distance.distance(tuple_list[i], centers_list[j]) < min_dist:
                min_dist = distance.distance(tuple_list[i], centers_list[j])
                current_center = centers_list[j]
        centers_dict[current_center].append(tuple_list[i])
    return_list = []
    for key in centers_dict:
        length = len(centers_dict[key])
        if length != 0:
            lat_sum = sum([x[0]] for x in centers_dict[key])
            lon_sum = sum([x[1]] for x in centers_dict[key])
            return_list.append((lat_sum / length, lon_sum / length))
    return return_list
