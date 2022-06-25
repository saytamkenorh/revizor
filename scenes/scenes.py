import pygame


class FrameStatus:
    clock: pygame.time.Clock
    surface: pygame.Surface
    events: list[pygame.event.Event]

    def __init__(
            self, clock: pygame.time.Clock,
            surface: pygame.Surface,
            events: list[pygame.event.Event]):
        self.clock = clock
        self.surface = surface
        self.events = events


class Scene:
    scene_status: 'SceneStatus'

    def __init__(self, scene_status: 'SceneStatus'):
        self.scene_status = scene_status

    def render(self, frame_status: FrameStatus):
        raise NotImplementedError()


class SceneStatus:
    scene: Scene
    scenes: dict[str, type[Scene]]

    def __init__(self):
        self.scene = None
        self.scenes = dict()

    def add_scene(self, name: str, scene: type[Scene]):
        if name in self.scenes:
            raise Exception("Scene name already in use")
        self.scenes[name] = scene

    def set_scene(self, name: str, *args):
        self.scene = self.scenes[name](self, *args)

    def render_current(self, frame_status: FrameStatus):
        self.scene.render(frame_status)

    def get_screen_size(self) -> tuple[int, int]:
        return pygame.display.get_window_size()
