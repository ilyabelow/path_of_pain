import pygame


# TODO move shared functionality here
class AdvancedSprite(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.y = 0
        self.drawing_group = None

    def draw(self, screen, offset):
        pass

    def fetch_layer(self, y=None):
        if self.drawing_group is None:
            for g in self.groups():
                if isinstance(g, AdvancedLayeredUpdates):
                    self.drawing_group = g
                    break
            else:
                raise BaseException('AdvancedSprite must be added to AdvancedLayeredUpdates')
        # y is None is used for static objects that does not change layers
        if y is not None:
            self.y = y
        self.drawing_group.change_layer(self, self.y // 50)  # TODO // 50? may be not?


class AdvancedLayeredUpdates(pygame.sprite.LayeredUpdates):
    def __init__(self, *sprites):
        pygame.sprite.LayeredUpdates.__init__(self, *sprites)

    def draw_all(self, surface, window):
        spritedict = self.spritedict
        dirty = self.lostsprites
        self.lostsprites = []
        dirty_append = dirty.append
        init_rect = self._init_rect
        for spr in self.sprites():
            rec = spritedict[spr]
            # it will try to use more specialized method for drawing sprites if there is one,
            # otherwise it will use standard method
            if hasattr(spr, 'draw'):
                newrect = spr.draw(surface, window)  # <---------------------- code insertion here
            else:
                newrect = surface.blit(spr.image, spr.rect)  # TODO add window support somewhere?
            if rec is init_rect:
                dirty_append(newrect)
            else:
                if newrect.colliderect(rec):
                    dirty_append(newrect.union(rec))
                else:
                    dirty_append(newrect)
                    dirty_append(rec)
            spritedict[spr] = newrect
        return dirty


    def add(self, *sprites, **kwargs):
        if not sprites:
            return
        if 'layer' in kwargs:
            layer = kwargs['layer']
        else:
            layer = None
        for sprite in sprites:
            if isinstance(sprite, AdvancedSprite):
                if not self.has_internal(sprite):
                    self.add_internal(sprite, layer)
                    sprite.add_internal(self)
                    if hasattr(sprite, 'fetch_layer'):  # can add non-Advanced sprites
                        sprite.fetch_layer()  # <--------------------------- code insertion here
            else:
                try:
                    self.add(*sprite, **kwargs)
                except (TypeError, AttributeError):
                    if hasattr(sprite, '_spritegroup'):
                        for spr in sprite.sprites():
                            if not self.has_internal(spr):
                                self.add_internal(spr, layer)
                                spr.add_internal(self)
                    elif not self.has_internal(sprite):
                        self.add_internal(sprite, layer)
                        sprite.add_internal(self)


class State:
    def __def__(self):
        self.app = None

    def update(self):
        pass

    def draw(self):
        pass

    # TODO shared method to fade in/out
