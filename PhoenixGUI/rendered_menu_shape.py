import pygame

class RenderedMenuShape:
    def __init__(self, pos, size, color, crop, type_, outline_width=None, outline_color=None, border_radius=0, width=0):
        self.pos = pos
        self.size = size
        self.color = color
        self.crop = crop
        self.type_ = type_
        self.outline_width = outline_width
        self.outline_color = outline_color
        self.border_radius = border_radius
        self.width = width

    def draw(self, screen):
        if self.type_ == "rect":
            self.draw_rect(screen)
        else:
            self.draw_circle(screen)

    def draw_rect(self, screen):
        s = pygame.Surface(self.size, pygame.SRCALPHA)
        pygame.draw.rect(s, 
                         self.color, 
                         pygame.Rect((0, 0), self.size),
                         border_radius=self.border_radius,
                         width=self.width)

        if self.outline_width != None and self.outline_color != None:
            pygame.draw.rect(s,
                             self.outline_color,
                             pygame.Rect((0, 0), self.size),
                             border_radius=self.border_radius,
                             width=self.outline_width)

        screen.blit(s, self.pos, self.crop)

    def draw_circle(self, screen):
        s = pygame.Surface(self.size, pygame.SRCALPHA)
        pygame.draw.ellipse(s, 
                            self.color, 
                            pygame.Rect((0, 0), self.size),
                            width=self.width)

        if self.outline_width != None and self.outline_color != None:
            pygame.draw.ellipse(s,
                                self.outline_color,
                                pygame.Rect((0, 0), self.size),
                                width=self.outline_width)

        screen.blit(s, self.pos, self.crop)