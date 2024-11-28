from concurrent.futures import thread
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
    """Create a double-pointed arrow centered at base_point and aligned with the direction vector."""
    # Normalize the direction vector
    direction = rs.VectorUnitize(direction)
    half_shaft_length = max(length * 0.5 - 4*radius, length * 0.05)  # Half the shaft length to center it
    cone_length = 4*radius

    # Offset base_point to center the cylinder
    cylinder_center = base_point
    cylinder_start = rs.PointAdd(cylinder_center, rs.VectorScale(direction, -half_shaft_length))
    cylinder_end = rs.PointAdd(cylinder_center, rs.VectorScale(direction, half_shaft_length))
    arrow1_start = rs.PointAdd(cylinder_center, rs.VectorScale(direction, (half_shaft_length+cone_length)))
    arrow2_start = rs.PointAdd(cylinder_center, rs.VectorScale(direction, -(half_shaft_length+cone_length)))

    # Create a plane aligned with the direction vector for the cylinder
    cylinder_plane = rs.PlaneFromNormal(cylinder_start, direction)

    # Create the cylinder (shaft)
    shaft = rs.AddCylinder(cylinder_plane, rs.Distance(cylinder_start, cylinder_end), radius, cap=True)
    print(color)
    rs.ObjectColor(shaft, color)

    # Calculate cone bases and tips for outward pointing cones
    cone1_base = arrow1_start  # Base at the end of the cylinder
    cone1_tip = rs.PointAdd(cone1_base, rs.VectorScale(direction, cone_length))  # Tip extends outward

    cone2_base = arrow2_start  # Base at the other end of the cylinder
    cone2_tip = rs.PointAdd(cone2_base, rs.VectorScale(direction, -cone_length))  # Tip extends outward

    # Create the cones
    cone1 = rs.AddCone(rs.PlaneFromNormal(cone1_base, -direction), cone_length, radius * 2, cap=True)
    rs.ObjectColor(cone1, color)

    cone2 = rs.AddCone(rs.PlaneFromNormal(cone2_base, direction), cone_length, radius * 2, cap=True)
    rs.ObjectColor(cone2, color)

    # Group the geometry
    group = rs.AddGroup()
    rs.AddObjectToGroup(shaft, group)
    rs.AddObjectToGroup(cone1, group)
    rs.AddObjectToGroup(cone2, group)
    return group

def visualize_principal_stresses_from_file(filepath):
    """Visualize principal stresses with arrows from a file."""
    with open(filepath, 'r') as file:
        reader = csv.DictReader(file)
        data = list(reader)

    SP_threshold = 0.1
    SP_factor = 5

    # Extract min and max stress values for color mapping
    stresses = [float(row["S1"]) for row in data] + [float(row["S2"]) for row in data] + [float(row["S3"]) for row in data]
    min_stress, max_stress = min(stresses), max(stresses)

    i=0
    # Create arrows
    for row in data:
        x, y, z = float(row["x"]), float(row["y"]), float(row["z"])
        S1, S2, S3 = float(row["S1"]), float(row["S2"]), float(row["S3"])

        if (abs(S1)>SP_threshold and abs(S2)>SP_threshold and abs(S3)>SP_threshold):

            SN1 = (float(row["SN1x"]), float(row["SN1y"]), float(row["SN1z"]))
            SN2 = (float(row["SN2x"]), float(row["SN2y"]), float(row["SN2z"]))
            SN3 = (float(row["SN3x"]), float(row["SN3y"]), float(row["SN3z"]))

            # Normalize principal directions
            SN1 = rs.VectorUnitize(SN1)
            SN2 = rs.VectorUnitize(SN2)
            SN3 = rs.VectorUnitize(SN3)

            i+=1
            print(i,S1, S2, S3)

            # Map stress values to colors
            color1 = map_to_color(S1, min_stress, max_stress)
            color2 = map_to_color(S2, min_stress, max_stress)
            color3 = map_to_color(S3, min_stress, max_stress)

            # Create arrows
            base_point = (x, y, z)
            create_arrow(base_point, SN1, abs(S1/SP_factor), 0.2, color1)
            create_arrow(base_point, SN2, abs(S2/SP_factor), 0.2, color2)
            create_arrow(base_point, SN3, abs(S3/SP_factor), 0.2, color3)

if __name__ == "__main__":
    # Path to your file
    filepath = r"C:\Rhino3D\Principal Stress Visualisation\StressData.csv"
    filepath = r"C:\Rhino3D\Principal Stress Visualisation\Gwalia_Grid_Red100p.csv"
    visualize_principal_stresses_from_file(filepath)