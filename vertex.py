class Vertex:
    def __init__(self, lat, lon, speed):
        self.lat = lat
        self.lon = lon
        self.speed = speed
        self.cost_to = -1
        self.father_id = ''
        self.neighbors = {}

    def add_neighbor(self, vertex, cost):
        if vertex in self.neighbors:
            self.neighbors[vertex][0] += 1
            self.neighbors[vertex][1] += cost
        else:
            self.neighbors[vertex] = [1, cost]

    def get_neighbors(self):
        return [x for x in self.neighbors]

    def get_id(self):
        return str(self.lat) + "," + str(self.lon) + "," + str(self.speed)

    def update_neighbors(self):  # function need editing
        for neighbor in self.neighbors:
            if neighbor.cost_to == -1 or self.cost_to + self.neighbors[neighbor] < neighbor.cost_to:
                neighbor.father_id = self.get_id()
                neighbor.cost_to = self.cost_to + self.neighbors[neighbor]

    def calculate_neighbor_dict(self):
        for neighbor in self.neighbors:
            self.neighbors[neighbor] = self.neighbors[neighbor][1] / self.neighbors[neighbor][0]

    def print_neighbors(self):
        for v in self.neighbors:
            print(str(v) + ' with cost=' + str(self.neighbors[v]))

    def __str__(self):
        return '(' + str(self.lat) + ',' + str(self.lon) + ') at ' + str(self.speed)

    def str2(self):
        str(self) + ' with cost_to=' + str(self.cost_to) + ' and father=' + self.father_id


class VertexFactory:
    def __init__(self):
        self.vertex_dict = {'start': Vertex(-200, -200, 0), 'end': Vertex(200, 200, 0)}
        self.vertex_dict['end'].cost_to = 0

    def get_vertex(self, lat, lon, speed):
        key = str(lat) + "," + str(lon) + "," + str(speed)
        if key not in self.vertex_dict:
            self.vertex_dict[key] = Vertex(lat, lon, speed)
        return self.vertex_dict[key]

    def get_vertex_by_id(self, vertex_id):
        return self.vertex_dict[vertex_id]

    def get_all_vertexes(self):
        return self.vertex_dict.values()

    def get_start(self):
        return self.vertex_dict['start']

    def get_end(self):
        return self.vertex_dict['end']

    def print_all_vertexes(self):
        for vertex in self.vertex_dict.values():
            print(vertex)

    def calculate_edge_costs(self):
        for key in self.vertex_dict:
            self.vertex_dict[key].calculate_neighbor_dict()
