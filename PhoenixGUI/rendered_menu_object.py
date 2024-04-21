class RenderedMenuObject:
    def __init__(self, image, pos, crop=None):
        self.image = image
        self.pos = pos
        self.crop = crop

    def draw(self, screen):
        if self.crop == None:
            screen.blit(self.image, self.pos)
        else:
            screen.blit(self.image, self.pos, self.crop)