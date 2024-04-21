from .util import update_pos_by_anchor

class MenuObject:
    def __init__(self, pos, max_size, anchor, layer=0, active=True):
        self.pos = pos
        self.max_size = max_size
        self.anchor = anchor
        self.layer = layer
        self.active = active
        self.render_flag = True

    def set_layer(self, layer):
        self.layer = layer

    def get_layer(self):
        return self.layer

    def set_pos(self, pos):
        self.pos = pos

    def get_pos(self):
        return self.pos

    def set_max_size(self, max_size):
        self.max_size = max_size

    def get_max_size(self):
        return self.max_size

    def set_anchor(self, anchor):
        self.anchor = anchor

    def get_anchor(self):
        return self.anchor

    def set_active(self, active):
        self.active = active

    def get_active(self):
        return self.active

    def enable(self):
        self.active = True

    def disable(self):
        self.active = False