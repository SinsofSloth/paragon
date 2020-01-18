from PySide2.QtCore import Signal
from PySide2.QtGui import QKeySequence
from PySide2.QtWidgets import QWidget, QGridLayout, QShortcut

from ui.map_cell import MapCell

TILE_TO_COLOR_STRING = {
    "TID_平地": "#8BC34A",
    "TID_橋": "#795548",
    "TID_河／平地": "#1565C0",
    "TID_無し": "#424242",
    "TID_林": "#1B5E20"
}


class MapGrid(QWidget):
    focused_spawn_changed = Signal(dict)

    def __init__(self):
        super().__init__()
        self.setContentsMargins(0, 0, 0, 0)
        self.cells = []
        self.selected_cells = []
        self.chapter_data = None
        self.selected_tile = None
        self.terrain_mode = False
        self.coordinate_key = "Coordinate (1)"

        layout = QGridLayout()
        for r in range(0, 32):
            row = []
            for c in range(0, 32):
                cell = self._create_cell(r, c)
                layout.addWidget(cell, r, c)
                row.append(cell)
            self.cells.append(row)
        layout.setVerticalSpacing(0)
        layout.setHorizontalSpacing(0)
        self.setLayout(layout)

        self.delete_shortcut = QShortcut(QKeySequence("Delete"), self)
        self.delete_shortcut.activated.connect(self._delete_selected_spawns)

    def _create_cell(self, r, c):
        cell = MapCell(r, c)
        cell.spawn_selected.connect(self._on_cell_selected)
        cell.spawn_selection_expanded.connect(self._on_cell_selection_expanded)
        cell.selected_for_move.connect(self._on_cell_selected_for_move)
        cell.tile_selected.connect(self._on_tile_selected)
        return cell

    def set_chapter_data(self, chapter_data):
        self.clear()
        if chapter_data:
            self._place_spawns(chapter_data.dispos)
            self._update_terrain(chapter_data.terrain)
        self.chapter_data = chapter_data

    def _refresh_dispos(self):
        dispos = self.chapter_data.dispos
        self.clear()
        self._place_spawns(dispos)

    def clear(self):
        self.selected_cells.clear()
        for r in range(0, 32):
            for c in range(0, 32):
                cell = self.cells[r][c]
                cell.clear_spawns()

    def _place_spawns(self, dispos):
        for faction in dispos.factions:
            for spawn in faction.spawns:
                coordinate = spawn[self.coordinate_key].value
                if coordinate[0] in range(0, 32) and coordinate[1] in range(0, 32):
                    target_cell = self.cells[coordinate[1]][coordinate[0]]
                    target_cell.place_spawn(spawn)

    def _update_terrain(self, new_terrain):
        for row in range(0, 32):
            for col in range(0, 32):
                tile_id = new_terrain.grid[row][col]
                tile = new_terrain.tiles[tile_id]
                self._update_cell_terrain(row, col, tile)

    def _update_cell_terrain(self, row, col, tile):
        tid = tile["TID"].value
        if tid in TILE_TO_COLOR_STRING:
            color_string = TILE_TO_COLOR_STRING[tid]
        else:
            color_string = "#424242"
        target_cell = self.cells[row][col]
        target_cell.set_color(color_string)

    def _on_cell_selected(self, selected_cell):
        for cell in self.selected_cells:
            cell.set_selected(False)
        self.selected_cells.clear()
        self.selected_cells.append(selected_cell)
        selected_cell.set_selected(True)
        self.focused_spawn_changed.emit(selected_cell.spawns[-1])

    def _on_cell_selection_expanded(self, cell):
        if cell not in self.selected_cells:
            self.selected_cells.append(cell)
            cell.set_selected(True)
            self.focused_spawn_changed.emit(cell.spawns[-1])

    def _on_cell_selected_for_move(self, cell):
        if not self.selected_cells:
            return
        origin = self.selected_cells[-1]
        delta_x = cell.column - origin.column
        delta_y = cell.row - origin.row
        if self._move_is_valid(delta_x, delta_y):
            self._perform_move(delta_x, delta_y)

    def _move_is_valid(self, delta_x, delta_y):
        for cell in self.selected_cells:
            new_x = cell.column + delta_x
            new_y = cell.row + delta_y
            if new_x not in range(0, 32) or new_y not in range(0, 32):
                return False
        return True

    def _perform_move(self, delta_x, delta_y):
        new_selected_cells_list = []
        for cell in self.selected_cells:
            new_x = cell.column + delta_x
            new_y = cell.row + delta_y
            self._move_top_spawn(cell, new_x, new_y)
            destination_cell = self.cells[new_y][new_x]
            new_selected_cells_list.append(destination_cell)

        self._refresh_dispos()
        self.selected_cells = new_selected_cells_list
        for cell in self.selected_cells:
            cell.set_selected(True)

    def _move_top_spawn(self, source, new_x, new_y):
        spawn = source.spawns[-1]
        coordinate = spawn[self.coordinate_key].value
        coordinate[0] = new_x
        coordinate[1] = new_y
        del source.spawns[-1]

    def _delete_selected_spawns(self):
        new_selected_cells_list = []
        for cell in self.selected_cells:
            spawn = cell.spawns[-1]
            self.chapter_data.dispos.delete_spawn(spawn)
            if len(cell.spawns) > 1:
                new_selected_cells_list.append(cell)

        self._refresh_dispos()
        self.selected_cells = new_selected_cells_list
        for cell in self.selected_cells:
            cell.set_selected(True)

    def transition_to_terrain_mode(self):
        self.terrain_mode = True
        self.selected_cells.clear()
        for r in range(0, 32):
            for c in range(0, 32):
                self.cells[r][c].transition_to_terrain_mode()

    def transition_to_dispos_mode(self):
        self.terrain_mode = False
        for r in range(0, 32):
            for c in range(0, 32):
                self.cells[r][c].transition_to_dispos_mode()

    def toggle_coordinate_key(self):
        if self.coordinate_key == "Coordinate (1)":
            self.coordinate_key = "Coordinate (2)"
        else:
            self.coordinate_key = "Coordinate (1)"
        self.selected_cells.clear()
        self._refresh_dispos()

    def _on_tile_selected(self, cell):
        if self.selected_tile:
            tile_id = self.selected_tile["ID"].value
            self.chapter_data.terrain.grid[cell.row][cell.column] = tile_id
            self._update_cell_terrain(cell.row, cell.column, self.selected_tile)

    def select_spawn(self, spawn):
        coordinate = spawn[self.coordinate_key].value
        cell = self.cells[coordinate[1]][coordinate[0]]
        self._on_cell_selected(cell)