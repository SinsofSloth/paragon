from enum import Enum

from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtCore import Signal
from PySide2.QtGui import QPixmap, QMouseEvent
from PySide2.QtWidgets import QLabel


class MapCellOccupationState(Enum):
    UNOCCUPIED = 0
    PLAYER = 1
    ENEMY = 2
    ALLIED = 3


_OCCUPATION_PIXMAPS = {
    MapCellOccupationState.UNOCCUPIED: None,
    MapCellOccupationState.PLAYER: "Assets/player.png",
    MapCellOccupationState.ENEMY: "Assets/enemy.png",
    MapCellOccupationState.ALLIED: "Assets/allied.png"
}

DEFAULT_BORDER = "1px dashed black"
SELECTED_BORDER = "2px solid black"


class MapCell(QLabel):
    selected_for_move = Signal(dict)
    spawn_selected = Signal(dict)
    spawn_selection_expanded = Signal(dict)
    tile_selected = Signal(dict)

    def __init__(self, row, column):
        super().__init__()
        self.setAlignment(QtGui.Qt.AlignCenter)
        self.row = row
        self.column = column
        self.spawns = []
        self.terrain_mode = False
        self._current_color = "#424242"
        self._current_border = DEFAULT_BORDER
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.setFixedSize(30, 30)
        self._refresh_stylesheet()

    def set_color(self, color_style_string):
        self._current_color = color_style_string
        self._refresh_stylesheet()

    def set_border(self, border):
        self._current_border = border
        self._refresh_stylesheet()

    def _refresh_stylesheet(self):
        params = (self._current_border, self._current_color)
        self.setStyleSheet("QLabel { border: %s; background-color: %s }" % params)

    def place_spawn(self, spawn):
        self.spawns.append(spawn)
        self._set_occupation_from_last_spawn()

    def pop_spawn(self):
        result = self.spawns.pop()
        self._set_occupation_from_last_spawn()
        return result

    def remove_spawn(self, spawn):
        if spawn in self.spawns:
            self.spawns.remove(spawn)
            self._set_occupation_from_last_spawn()

    def clear_spawns(self):
        self.spawns.clear()
        self.clear()
        self.set_border(DEFAULT_BORDER)

    def set_selected(self, is_selected):
        if is_selected:
            self.set_border(SELECTED_BORDER)
        else:
            self.set_border(DEFAULT_BORDER)

    def _set_occupation_from_last_spawn(self):
        if not self.spawns:
            self.clear()
            return
        last_spawn = self.spawns[-1]
        team = last_spawn["Team"].value
        if team == 0:
            occupation_state = MapCellOccupationState.PLAYER
        elif team == 1:
            occupation_state = MapCellOccupationState.ENEMY
        else:
            occupation_state = MapCellOccupationState.ALLIED
        self.setPixmap(QPixmap(_OCCUPATION_PIXMAPS[occupation_state]))

    def mousePressEvent(self, ev: QMouseEvent):
        if self.terrain_mode:
            self.tile_selected.emit(self)
        else:
            self._handle_mouse_press_event_for_dispos(ev)

    def _handle_mouse_press_event_for_dispos(self, ev: QMouseEvent):
        if ev.button() != QtCore.Qt.LeftButton:
            return
        if not self.spawns:
            self.selected_for_move.emit(self)
        elif ev.modifiers() & QtCore.Qt.ControlModifier == QtCore.Qt.ControlModifier:
            self.spawn_selection_expanded.emit(self)
        else:
            self.spawn_selected.emit(self)

    def transition_to_terrain_mode(self):
        self.terrain_mode = True
        self.set_border(DEFAULT_BORDER)

    def transition_to_dispos_mode(self):
        self.terrain_mode = False
