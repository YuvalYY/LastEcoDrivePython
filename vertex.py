class Vertex:
    def __init__(self, lat, lon, speed):
        self.lat = lat
        self.lon = lon
        self.speed = speed
        self.cost_to = -1
        self.neighbors = []

    def add_neighbor(self, vertex, cost):
        self.neighbors.append([vertex, cost])

    def get_neighbors(self):
        return [x[0] for x in self.neighbors]

    def print_neighbors(self):
        for v in self.neighbors:
            print(str(v[0]) + ' with cost=' + str(v[1]))

    def __str__(self):
        return '(' + str(self.lat) + ',' + str(self.lon) + ') at ' + str(self.speed)


class VertexFactory:
    def __init__(self):
        self.vertex_dict = {'start': Vertex(-200, -200, 0), 'end': Vertex(200, 200, 0)}

    def get_vertex(self, lat, lon, speed):
        key = str(lat) + "," + str(lon) + "," + str(speed)
        if key not in self.vertex_dict:
            self.vertex_dict[key] = Vertex(lat, lon, speed)
        return self.vertex_dict[key]

    def get_all_vertexes(self):
        return self.vertex_dict.values()

    def get_start(self):
        return self.vertex_dict['start']

    def get_end(self):
        return self.vertex_dict['end']
#
