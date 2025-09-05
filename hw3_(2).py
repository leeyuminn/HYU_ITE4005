import sys
import numpy as np
import math

class point:
    def __init__(self, id, x_coord, y_coord):
        self.id = int(id)
        self.x_coord = float(x_coord)
        self.y_coord = float(y_coord)
        self.label = None

    def set_label(self, label):
        self.label = int(label)

    def get_label(self):
        return self.label

def read_inputfile(input_file):
    points = []
    with open(input_file, 'r') as file:
        for line in file:
            id, x_coord, y_coord = line.strip().split('\t')
            points.append(point(id, float(x_coord), float(y_coord)))
    return points

def make_distance_table(points):
    num_points = len(points)
    distance_table = np.zeros((num_points, num_points))
    for i in range(num_points):
        for j in range(num_points):
            dx = points[j].x_coord - points[i].x_coord
            dy = points[j].y_coord - points[i].y_coord
            distance_table[i, j] = math.sqrt((dx*dx) + (dy*dy))
    return distance_table

def find_neighbors(points, distance_table, core_id, eps):
    neighbors = []
    for j in range(len(points)):
        if j == core_id: 
            continue 
        if distance_table[core_id][j] < eps:
            neighbors.append(points[j])          
    return neighbors

def db_scan(points, distance_table, eps, min_pts):
    current_label = -1

    # iterate over every point
    for point in points:
        # skip processed points
        if point.get_label() is not None:
            continue
        # find initial neighbors
        neighbors = find_neighbors(points, distance_table, point.id, eps)
    
        if len(neighbors) < min_pts:
            point.set_label(-1) # Non-core points are noise
            continue
        
        # start a new cluster
        current_label += 1
        point.set_label(current_label) 

        # expand neighborhood
        seed_set = neighbors 

        for neighbor_point in seed_set:
            if neighbor_point.get_label() == -1: #noise
                neighbor_point.set_label(current_label)
            if neighbor_point.get_label() != None:
                continue
            
            nb_neighbors = find_neighbors(points, distance_table, neighbor_point.id, eps)
            neighbor_point.set_label(current_label)

            # Core-point check
            if len(nb_neighbors) < min_pts:
                continue
            seed_set.extend(nb_neighbors)

def make_outputfile(points, n, inputfile_name):
    labels = {}
    for point in points:
        lb = point.get_label()
        if lb not in labels:
            if lb == -1: #noise
                continue
            labels[lb] = []
        labels[lb].append(point.id)

    cluster_list = list(labels.values())
    sort_cluster_list = sorted(cluster_list, key=len, reverse=True)

    for i in range(n):
        outputfile_name = inputfile_name.split('.')[0] + '_cluster_' + str(i) + '.txt'
        with open(outputfile_name, 'w') as file:
            for point_id in sort_cluster_list[i]:
                file.write(str(point_id) + '\n')

def main():
    input_file = sys.argv[1]
    num_cluster = int(sys.argv[2])
    eps = int(sys.argv[3])
    min_pts = int(sys.argv[4]) 

    points = read_inputfile(input_file)
    distance_table = make_distance_table(points)
    db_scan(points, distance_table, eps, min_pts)
    make_outputfile(points, num_cluster, input_file)

if __name__=="__main__":
    main()
