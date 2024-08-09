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

    def get_id(self):
        return self.id

    def get_xcoord(self):
        return self.x_coord

    def get_ycoord(self):
        return self.y_coord

def read_inputfile(inputfile):
    points = []
    with open(inputfile, 'r') as file:
        for line in file:
            id, x_coord, y_coord = line.strip().split('\t')
            points.append(point(id, float(x_coord), float(y_coord)))
    return points

def dbscan(points, dist_matrix, eps, minPts):
    num_points = len(points)
    cur_cluster_label = -1

    for point in points:
        # 이미 정의된 포인트는 건너뛰어
        if point.get_label() is not None:
            continue
        # 정의 안된 포인트면, find Neighborhood of points[i]
        neighbors = find_neighborhood(points, dist_matrix, point.get_id(), eps)

        if len(neighbors) < minPts: # then, == border or outlier
            # label(point) <- Noise
            point.set_label(-1) 
            continue
        
        # 아니라면 core point라는 거니까 -> start a new cluster
        cur_cluster_label += 1
        point.set_label(cur_cluster_label) 

        # expand neighborhood
        seed_set = neighbors 

        for nb_point in seed_set:
            if nb_point.get_label() == -1:
                nb_point.set_label(cur_cluster_label)
            if nb_point.get_label() != None:
                continue
            
            # 또 core point 조건을 만족하는 point가 있는지 확인
            nb_neighbors = find_neighborhood(points, dist_matrix, nb_point.get_id(), eps)
            nb_point.set_label(cur_cluster_label)

            if len(nb_neighbors) < minPts:
                continue
            seed_set.extend(nb_neighbors)
    
def find_neighborhood(points, dist_matrix, core_index, eps):
    N = []
    for j in range(len(points)):
        if j == core_index: continue # 자신 제외
        if dist_matrix[core_index][j] < eps:
            N.append(points[j])   
    return N

def make_dist_matrix(points):
    num_points = len(points)
    dist_matrix = np.zeros((num_points, num_points))
    for i in range(num_points):
        for j in range(num_points):
            dist_matrix[i, j] = calc_distance(points[i], points[j])
    return dist_matrix


def calc_distance(pt1, pt2):
    a = pt2.get_xcoord() - pt1.get_xcoord()
    b = pt2.get_ycoord() - pt1.get_ycoord()
    distance = math.sqrt((a*a) + (b*b)) # 피타고라스 
    return distance

def make_outputfile(points, n, inputfile_name):
    label_groups = {}
    for point in points:
        pt_label = point.get_label()
        if pt_label not in label_groups:
            # noise 클러스터는 제외
            if pt_label == -1:
                continue
            label_groups[pt_label] = []
        label_groups[pt_label].append(point.get_id())
    #print(label_groups.keys())

    # sort
    clusterlist = list(label_groups.values())
    sort_clusterlist = sorted(clusterlist, key=len, reverse=True)

    # 출력파일 생성
    for i in range(n):
        outputfile_name = inputfile_name.split('.')[0] + '_cluster_' + str(i) + '.txt'
        
        with open(outputfile_name, 'w') as file:
            for point_id in sort_clusterlist[i]:
                file.write(str(point_id) + '\n')

def main():
    inputfile = sys.argv[1]
    clusters_num = int(sys.argv[2])
    eps = int(sys.argv[3]) #radius
    minPts = int(sys.argv[4]) #minimum points

    points = read_inputfile(inputfile)

    # create dist_matrix
    dist_matrix = make_dist_matrix(points)
    # start dbscan
    dbscan(points, dist_matrix, eps, minPts)

    make_outputfile(points, clusters_num, inputfile)


if __name__=="__main__":
    main()
