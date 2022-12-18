import networkx as nx
import numpy as np
import plotly.graph_objs as go
import trimesh


def get_soccer_points(subdivisions):
    # Initialization
    sphere = trimesh.creation.icosphere(subdivisions=subdivisions)
    graph = sphere.vertex_adjacency_graph
    key_point_distance = 1 << subdivisions
    is_vertex_black = np.full(len(sphere.vertices), False)

    # Black pieces on soccer ball.
    for u in range(12):  # The first 12 vertices are from the original icosahedron.
        is_vertex_black[u] = True
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


if __name__ == "__main__":
    # Generate points.
    black_points, white_points = get_soccer_points(4)

    # Visualize points.
    black_scatters = go.Scatter3d(
        x=black_points[:, 0], y=black_points[:, 1], z=black_points[:, 2],
        mode='markers',
        marker=dict(
            size=16,
            color='black'
        ),
        name="black points"
    )
    white_scatters = go.Scatter3d(
        x=white_points[:, 0], y=white_points[:, 1], z=white_points[:, 2],
        mode='markers',
        marker=dict(
            size=16,
            color='white'
        ),
        name="white points"
    )
    fig = go.Figure(data=[black_scatters, white_scatters])
    fig.show()
