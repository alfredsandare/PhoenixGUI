class Hitbox:
    def __init__(self, left, top, right, bottom):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom

    def is_pos_inside(self, x, y):
        return self.left <= x <= self.right and self.top <= y <= self.bottom

    def __str__(self):
        return f"Hitbox({self.left}, {self.top}, {self.right}, {self.bottom})"
