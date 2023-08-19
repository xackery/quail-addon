
class ModelVertex():
    position = []  # type: list[float]
    normal = []  # type: list[float]
    uv = []  # type: list[float]
    color = []  # type: list[int]


class ModelTriangle():
    indices = []  # type: list[int]
    material = ''  # type: str
    flags = 0  # type: int


class Model():
    name = ""  # type: str
    ext = "mod"  # type: str
    vertices = {}  # type: dict[int, ModelVertex]
    triangles = {}  # type: dict[int, ModelTriangle]

    def __init__(self, name: str):
        self.name = name
        self.vertices = {}
        self.triangles = {}

    def add_vertex(self, position: list[float], normal: list[float], uv: list[float], color: list[int]) -> int:
        for i, j in enumerate(self.vertices):
            v = self.vertices.get(i)
            if v is None:
                continue
            if position != v.position or normal != v.normal or uv != v.uv:
                continue
            return i
        index = len(self.vertices)
        self.vertices[index] = ModelVertex()
        self.vertices[index].position = position
        self.vertices[index].normal = normal
        self.vertices[index].uv = uv
        self.vertices[index].color = color
        return index

    def add_triangle(self, indices: list[int], material: str, flags: int) -> int:
        for i, t in enumerate(self.triangles):
            t = self.triangles.get(i)
            if t is None:
                continue
            if indices != t.indices:
                continue
            return i
        triangle = ModelTriangle()
        triangle.indices = indices
        triangle.material = material
        triangle.flags = flags
        index = len(self.triangles)
        self.triangles[index] = triangle
        return index

    def write(self, quail_path: str) -> bool:
        mesh_path = "%s/%s.mesh" % (quail_path, self.name)

        vw = open("%s/vertex.txt" % mesh_path, "w")
        vw.write("position|normal|uv|uv2|tint\n")

        tw = open("%s/triangle.txt" % mesh_path, "w")
        tw.write("index|flag|material_name\n")

        tw.write("ext|%s|-1\n" % self.ext)

        for k in self.vertices:
            vert = self.vertices.get(k)
            if vert is None:
                continue

            vw.write("%0.8f,%0.8f,%0.8f|" % (
                vert.position[:]))
            vw.write("%0.8f,%0.8f,%0.8f|" % (
                vert.normal[:]))
            vw.write("%0.8f,%0.8f|" % (vert.uv[0], vert.uv[1]+1))
            vw.write("%0.8f,%0.8f|" % (0, 0))
            vw.write("%d,%d,%d,%d\n" % vert.color)

        for k in self.triangles:
            tri = self.triangles.get(k)
            if tri is None:
                continue
            tw.write("%s|" % ",".join(map(str, tri.indices)))
            tw.write("%d|%s\n" %
                     (tri.flags, tri.material))
        tw.close()
        vw.close()
        return True
