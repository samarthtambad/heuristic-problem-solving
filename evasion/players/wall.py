
class Wall:
    def __init__(self):
        pass

    def occupies(self, px, py) -> bool:
        pass


class HorizontalWall(Wall):
    def __init__(self, y, x1, x2):
        super().__init__()
        self.y = y
        self.x1 = x1
        self.x2 = x2

    def occupies(self, px, py) -> bool:
        return py == self.y and self.x1 <= px <= self.x2

    def __repr__(self):
        return "0 {0} {1} {2}".format(self.y, self.x1, self.x2)


class VerticalWall(Wall):
    def __init__(self, x, y1, y2):
        super().__init__()
        self.x = x
        self.y1 = y1
        self.y2 = y2

    def occupies(self, px, py) -> bool:
        return px == self.x and self.y1 <= py <= self.y2

    def __repr__(self):
        return "1 {0} {1} {2}".format(self.x, self.y1, self.y2)


class DiagonalWall(Wall):
    def __init__(self, x1, x2, y1, y2, build_direction):
        super().__init__()
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.build_direction = build_direction

    def occupies(self, px, py) -> bool:
        if self.build_direction == 1:
            offset = px - self.x1
            return (self.y1 + offset == py or self.y1 + offset + 1 == py) and self.x1 <= px <= self.x2 and self.y1 <= py <= self.y2

        offset = py - self.y1
        return (self.x1 + offset == px or self.x1 + offset + 1 == px) and self.x1 <= px <= self.x2 and self.y1 <= py <= self.y2

    def __repr__(self):
        return "2 {0} {1} {2} {3} {4}".format(self.x1, self.x2, self.y1, self.y2, self.build_direction)
