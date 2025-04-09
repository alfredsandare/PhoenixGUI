import math
import pygame
from PhoenixGUI.menu_object import MenuObject
from PhoenixGUI.rendered_menu_object import RenderedMenuObject


class PieChart(MenuObject):
    def __init__(self, pos,  radius, slices, colors, max_size=None, anchor="nw",
                 layer=0, active=True, hover_text=None):
        super().__init__(pos, max_size, anchor, layer, active, hover_text)
        self.radius = radius
        self.slices = slices
        self.colors = colors

        if not (0.999 < sum(self.slices) < 1.001):
            raise Exception(f"Sum of slices must be 1, not{sum(self.slices)}")

    def render(self, menu_pos, menu_size, ui_size, scroll, font_path=None):
        surface = pygame.Surface((2*self.radius, 2*self.radius), pygame.SRCALPHA)

        sum_of_previous_slices = 0
        for i, slice_share in enumerate(self.slices):
            points = [(self.radius, self.radius)]
            resolution = round(2 * math.pi * self.radius * slice_share)
            for j in range(resolution):
                angle = (sum_of_previous_slices + slice_share*j/resolution) * 2 * math.pi
                x = self.radius + int(self.radius * math.cos(angle))
                y = self.radius + int(self.radius * math.sin(angle))

                points.append((x, y))
            points.append((self.radius, self.radius))

            if i >= len(self.colors):
                raise Exception("Not enough colors in Piechart")

            pygame.draw.polygon(surface, self.colors[i], points)
            sum_of_previous_slices += slice_share

        crop, pos = self._adjust_pos_and_crop(self.pos, surface.get_size(),
                                              menu_pos, menu_size, scroll)

        return RenderedMenuObject(surface, pos, crop)
