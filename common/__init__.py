from mathutils import Vector, Quaternion


def string_to_vector(line: str) -> Vector:
    lines = line.split(",")
    return Vector((float(lines[0]), float(lines[1]), float(lines[2])))


def string_to_quaternion(line: str) -> Quaternion:
    lines = line.split(",")
    return Quaternion((float(lines[0]), float(lines[1]), float(lines[2]), float(lines[3])))
