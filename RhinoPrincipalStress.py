import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino
import System
import csv

rgbBase = [0,0,0]

def intcolor(rgbInc):
    "increments global rgb variable with modulo 255"
    
    global rgbBase

    for i in range(3): 
        rgbBase[i] = (rgbBase[i] + rgbInc[i]) %255
    red, green, blue = rgbBase
    return System.Drawing.Color.FromArgb(red, green, blue)

def map_to_color(value, min_value, max_value):
    """Map a scalar value to a rainbow color scale."""
    t = (value - min_value) / (max_value - min_value)
    t = max(0, min(1, t))  # Clamp t to the range [0, 1]

    # Define the rainbow gradient as RGB values
    if t < 0.2:
        r, g, b = 255, int(255 * (t / 0.2)), 0
    elif t < 0.4:
        r, g, b = int(255 * (1 - (t - 0.2) / 0.2)), 255, 0
    elif t < 0.6:
        r, g, b = 0, 255, int(255 * ((t - 0.4) / 0.2))
    elif t < 0.8:
        r, g, b = 0, int(255 * (1 - (t - 0.6) / 0.2)), 255
    else:
        r, g, b = int(255 * ((t - 0.8) / 0.2)), 0, 255

    return System.Drawing.Color.FromArgb(r, g, b)

def create_arrow(base_point, direction, length, radius, color):
    """Create a double-pointed arrow."""
    cylinder_height = length * 0.8
    cone_height = length * 0.1

    # Create the cylinder (shaft)
    start_cylinder = rs.AddCylinder(base_point, cylinder_height, radius)
    rs.ObjectColor(start_cylinder, color)

    # Create cones (tips)
    cone_base1 = rs.CopyObject(base_point, direction * cylinder_height)
    cone_tip1 = rs.CopyObject(cone_base1, direction * cone_height)
    cone_base2 = rs.CopyObject(base_point, -direction * cylinder_height)
    cone_tip2 = rs.CopyObject(cone_base2, -direction * cone_height)
    tip1 = rs.AddCone(cone_base1, cone_tip1, radius * 2)
    tip2 = rs.AddCone(cone_base2, cone_tip2, radius * 2)

    # Group the geometry
    group = rs.AddGroup()
    rs.AddObjectToGroup(start_cylinder, group)
    rs.AddObjectToGroup(tip1, group)
    rs.AddObjectToGroup(tip2, group)
    return group

def visualize_principal_stresses_from_file(filepath):
    """Visualize principal stresses with arrows from a file."""
    with open(filepath, 'r') as file:
        reader = csv.DictReader(file)
        data = list(reader)

    # Extract min and max stress values for color mapping
    stresses = [float(row["S1"]) for row in data] + [float(row["S2"]) for row in data] + [float(row["S3"]) for row in data]
    min_stress, max_stress = min(stresses), max(stresses)

    # Create arrows
    for row in data:
        x, y, z = float(row["x"]), float(row["y"]), float(row["z"])
        S1, S2, S3 = float(row["S1"]), float(row["S2"]), float(row["S3"])
        SN1 = (float(row["SN1x"]), float(row["SN1y"]), float(row["SN1z"]))
        SN2 = (float(row["SN2x"]), float(row["SN2y"]), float(row["SN2z"]))
        SN3 = (float(row["SN3x"]), float(row["SN3y"]), float(row["SN3z"]))

        # Normalize principal directions
        SN1 = rs.VectorUnitize(SN1)
        SN2 = rs.VectorUnitize(SN2)
        SN3 = rs.VectorUnitize(SN3)

        # Map stress values to colors
        color1 = map_to_color(S1, min_stress, max_stress)
        color2 = map_to_color(S2, min_stress, max_stress)
        color3 = map_to_color(S3, min_stress, max_stress)

        # Create arrows
        base_point = (x, y, z)
        create_arrow(base_point, SN1, abs(S1), 0.1, color1)
        create_arrow(base_point, SN2, abs(S2), 0.1, color2)
        create_arrow(base_point, SN3, abs(S3), 0.1, color3)

if __name__ == "__main__":
    # Path to your file
    filepath = r"C:\Rhino3D\Principal Stress Visualisation\StressData.csv"
    visualize_principal_stresses_from_file(filepath)