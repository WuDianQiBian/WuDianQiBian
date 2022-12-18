import colorama
import networkx as nx
import numpy as np
import scipy.spatial.transform
import trimesh

SCREEN_SIZE = 72                                     # Output size is (SCREEN_SIZE, SCREEN_SIZE)
ILLUMINATION = ".,-~:;=!*#$@"                        # Characters for lighting
K = 190                                              # Camera is positioned at (0, 0, -K)
SPHERE_CENTER = np.array([0, 0, -184])               # The center of sphere
L = np.array([0, -np.sqrt(2) / 2, -np.sqrt(2) / 2])  # Direction towards light source

def get_soccer_points(subdivisions):
    # Initialization
    sphere = trimesh.creation.icosphere(subdivisions=subdivisions)
    graph = sphere.vertex_adjacency_graph
    key_point_distance = 1 << subdivisions
    is_vertex_black = np.full(len(sphere.vertices), False)

    # Black pieces on soccer ball.
    for u in range(12):  # The first 12 vertices are from the original icosahedron.
        for _, v in nx.bfs_edges(graph, u, depth_limit=key_point_distance // 3):
            is_vertex_black[v] = True

    # Black strips connecting two black pieces.
    for u in range(12):
        shortest_path = nx.single_source_shortest_path(graph, u, key_point_distance)
        for v in range(u + 1, 12):
            if v in shortest_path:
                is_vertex_black[shortest_path[v]] = True

    # Construct black and white points.
    black_points = sphere.vertices[is_vertex_black]
    white_points = sphere.vertices[~is_vertex_black]
    return black_points, white_points


def draw_points(points, is_black, output):
    for point in points:
        normal = point - SPHERE_CENTER

        # Skip if the point is occluded.
        if np.dot(normal, np.array([0, 0, -K]) - point) < 0:
            continue

        # Project to screen.
        xp = int(point[0] * K / (K + point[2]) + SCREEN_SIZE / 2)
        yp = int(point[1] * K / (K + point[2]) + SCREEN_SIZE / 2)

        # Set it to ' ' if is_black.
        if is_black:
            output[yp, xp] = ' '
            continue

        # Add lighting otherwise.
        l = np.dot(normal, L)
        if l < 0:
            l = 0  # add some light to the dark part.
        luminance_index = int(l * (len(ILLUMINATION) - 1))
        output[yp, xp] = ILLUMINATION[luminance_index]



if __name__ == "__main__":
    # Init terminal display.
    colorama.init()
    print('\033[?25l', end="")

    # Generate points on soccer sphere.
    black_points, white_points = get_soccer_points(6)

    # Let's roll!
    for i in np.arange(0, 100, 0.1):
        print("\x1b[H")  # Need this in Windows system.
        output = np.full((SCREEN_SIZE, SCREEN_SIZE), " ")
        rotation_matrix = scipy.spatial.transform.Rotation.from_euler('y', i).as_matrix()
        draw_points(white_points @ rotation_matrix.T + SPHERE_CENTER, False, output)
        draw_points(black_points @ rotation_matrix.T + SPHERE_CENTER, True, output)
        print(*[''.join(np.repeat(row, 2)) for row in output], sep="\n")
