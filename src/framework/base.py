"""
Module with some low-level base classes
"""

import pygame


# TODO move some shared functionality here?
class AdvancedSprite(pygame.sprite.Sprite):
    """
    Spite with support of LAYERS and COMPLEX DRAWING
    """

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.render_group = None

    def draw(self, screen, window):
        """
        Draw sprite on some surface
        Here, complex rendering logic should be placed (if your sprite's picture will be updated every frame)
        screen.blit should be called here

        :param screen: Surface to draw on
        :param window: Game window to offset drawing coordinates accordingly
        :return: Rect on which sprite has been drawn onto
        """
        pass

    def fetch_layer(self, y):
        """
        Update sprite's layer
        This method is just a pretty wrapper around AdvancedLayeredUpdates.change layer.
        May be actually useless
        Will fall if render_group is not initialized

        :param y: y *coordinate* of the sprite
        :return: None
        """
        self.render_group.change_layer(self, y // 50)  # TODO // 50? may be not?

    def postponed_fetch_layer(self, y):
        """
        To fetch layer inside Sprite.__init__. Layer will be fetched inside AdvancedLayeredUpdates.add

        :param y:
        :return:
        """
        self.postponed_y = y


class AdvancedLayeredUpdates(pygame.sprite.LayeredUpdates):
    """
    LayeredUpdates with rewritten draw() function that first tries to call sprite-specific draw method.
    Adding usual Sprites is supported.
    Also automatic AdvancedSprite additional init is performed
    """

    def __init__(self, *sprites):
        pygame.sprite.LayeredUpdates.__init__(self, *sprites)

    def draw_all(self, surface, window):
        """
        Draws all the sprites
        Works the same as draw function from base class but it can call sprite-specific draw method
        plus it grabs window param

        :param surface: Surface to draw on
        :param window: Game window that will be passed to AdvancedSprite.draw method
        :return: Rects that was redrawn
        """
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
                # in case we work with default sprite
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
        """
        Adds sprites to the group
        Works the same as add function from base class but it can take AdvancedSprite natively and it can
        initialize render_group field of a sprite with self

        :param sprites: Sprites to add
        :param kwargs: No idea, copypasted from base class
        :return: None
        """
        if not sprites:
            return
        if 'layer' in kwargs:
            layer = kwargs['layer']
        else:
            layer = None
        for sprite in sprites:
            # code insertion here -------v
            if isinstance(sprite, AdvancedSprite) or isinstance(sprite, pygame.sprite.Sprite):
                if not self.has_internal(sprite):
                    self.add_internal(sprite, layer)
                    sprite.add_internal(self)
                    if hasattr(sprite, 'render_group'):  # redundant?
                        sprite.render_group = self  # <-------------------- code insertion here
                    if hasattr(sprite, 'postponed_y') and hasattr(sprite, 'fetch_layer'):
                        sprite.fetch_layer(sprite.postponed_y)
                        del sprite.postponed_y
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


# TODO move more functionality here?
class State:
    """
    Base class for application states: Menu and Game
    """

    def __def__(self):
        self.app = None

    def update(self):
        """
        Update all objects that are held in the state

        :return: None
        """
        pass

    def draw(self):
        """
        Draw all objects that are held in the state

        :return: None
        """
        pass

    # TODO shared method to fade in/out
