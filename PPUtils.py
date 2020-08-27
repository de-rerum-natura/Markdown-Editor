
def convert_point_ts_to_tk(point):
    # conversion from ts to tk text widget. in tk lines start with 1, in ts with 0
    line = point[0] + 1
    return "{}.{}".format(line, point[1])

def convert_point_tk_to_ts(index):
        # conversion from tk text widget to ts. In ts lines start with 0, in tk with 1
        split_string = index.split(".")
        int_tuple = (int(split_string[0])-1, int(split_string[1]))
        return int_tuple

def ts_points_find_larger (point1, point2):
    if (point1[0] > point2[0]):
        return point1
    elif (point2[0] > point1[0]):
        return point2
    else:
        if (point1[1] > point2[1]):
            return point1
        elif (point1[1] < point2[1]):
            return point2
        else:
            return None