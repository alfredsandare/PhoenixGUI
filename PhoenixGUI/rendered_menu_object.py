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

    def get_image_size(self):
        return self.image.get_size()

    def get_cropped_image_size(self):
        if self.crop is None:
            return self.image.get_size()

        return [self.crop[2]-self.crop[0], self.crop[3]-self.crop[1]]
