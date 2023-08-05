import islpy as isl

ctx = isl.Context()
space = isl.Space.create_from_names(ctx, set=["x", "y"])

bset = (isl.BasicSet.universe(space)
        .add_constraint(isl.Constraint.ineq_from_names(space, {1: -1, "x":1}))
        .add_constraint(isl.Constraint.ineq_from_names(space, {1: 5, "x":-1}))
        .add_constraint(isl.Constraint.ineq_from_names(space, {1: -1, "y": 1}))
        .add_constraint(isl.Constraint.ineq_from_names(space, {1: 5, "y": -1})))
print "set 1:", bset

bset2 = isl.BasicSet("{[x, y] : x >= 0 and x < 5 and y >= 0 and y < x+4 }")
print "set 2:", bset2

bsets_in_union = []
bset.union(bset2).coalesce().foreach_basic_set(bsets_in_union.append)
union, = bsets_in_union
print "union:", union
# ENDEXAMPLE

import matplotlib.pyplot as pt

def plot_basic_set(bset, *args, **kwargs):
    # This is a total hack. But it works for what it needs to do. :)

    plot_vert = kwargs.pop("plot_vert", False)

    vertices = []
    bset.compute_vertices().foreach_vertex(vertices.append)

    vertex_pts = []

    for v in vertices:
        points = []
        isl.Set.from_basic_set(v.get_expr()).foreach_point(points.append)
        point, = points
        vertex_pts.append([
            int(point.get_coordinate(isl.dim_type.set, i)) for i in range(2)])

    import numpy as np
    vertex_pts = np.array(vertex_pts)

    center = np.average(vertex_pts, axis=0)

    from math import atan2
    vertex_pts = np.array(
            sorted(vertex_pts, key=lambda (x, y): atan2(y-center[0], x-center[1])))

    if plot_vert:
        pt.plot(vertex_pts[:,0], vertex_pts[:,1], "o")

    import matplotlib.path as mpath
    import matplotlib.patches as mpatches

    Path = mpath.Path

    codes = [Path.LINETO] * len(vertex_pts)
    codes[0] = Path.MOVETO

    pathdata = [
        (code, tuple(coord)) for code, coord in zip(codes, vertex_pts)]
    pathdata.append((Path.CLOSEPOLY, (0, 0)))

    codes, verts = zip(*pathdata)
    path = mpath.Path(verts, codes)
    patch = mpatches.PathPatch(path, **kwargs)
    pt.gca().add_patch(patch)


plot_basic_set(bset, facecolor='red', edgecolor='black', alpha=0.3)
plot_basic_set(bset2, facecolor='green', edgecolor='black', alpha=0.2)
pt.grid()
pt.xlim([-1, 6])
pt.ylim([-1, 8])
#pt.show()
pt.savefig("before-union.png", dpi=50)

plot_basic_set(union, facecolor='blue', edgecolor='yellow', alpha=0.5, plot_vert=True)
pt.savefig("after-union.png", dpi=50)
