import logging

from PySide2 import QtCore
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QInputDialog

from paragon.model.game import Game
from paragon.model.multi_model import MultiModel
from paragon.ui.auto_widget_generator import AutoWidgetGenerator

from paragon.model.node_model import NodeModel
from paragon.ui.controllers.about import About
from paragon.ui.controllers.fe15_main_widget import FE15MainWidget
from paragon.ui.views.ui_main_window import Ui_MainWindow


class MainWindow(Ui_MainWindow):
    def __init__(self, ms, gs):
        super().__init__()
        self.ms = ms
        self.gs = gs
        self.gen = AutoWidgetGenerator(ms, gs)
        self.about_dialog = About()
        self.open_uis = {}

        node_model = NodeModel(gs.data)
        multi_model = MultiModel(gs.data)
        self.nodes_list.setModel(node_model)
        self.multis_list.setModel(multi_model)

        self.nodes_list.activated.connect(self._on_node_activated)
        self.multis_list.activated.connect(self._on_multi_activated)
        self.save_action.triggered.connect(self._on_save)
        self.reload_action.triggered.connect(self._on_reload)
        self.close_action.triggered.connect(self._on_close)
        self.quit_action.triggered.connect(self.close)
        self.about_action.triggered.connect(self._on_about)

        self._add_main_widget()

    def _add_main_widget(self):
        g = self.gs.project.game
        if g == Game.FE15:
            main_widget = FE15MainWidget(self.ms, self.gs, self)
            self.splitter.addWidget(main_widget)
            self.splitter.setStretchFactor(1, 1)

    def _on_close(self):
        self.ms.sm.transition("SelectProject", main_state=self.ms)

    def _on_reload(self):
        self.ms.sm.transition("Load", main_state=self.ms, project=self.gs.project)

    def _on_save(self):
        try:
            logging.debug("Save started.")
            self.gs.data.write()
            logging.debug("Save completed.")
        except:
            logging.exception("Save failed.")
            # TODO: Show a dialog.

    def _on_about(self):
        self.about_dialog.show()

    def _on_node_activated(self, index):
        node = self.nodes_list.model().data(index, QtCore.Qt.UserRole)
        self.open_node(node)

    def open_node_by_id(self, node_id):
        return self.open_node(self.nodes_list.model().get_by_id(node_id))

    def open_node(self, node):
        # Check if the UI was generated previously.
        if node in self.open_uis:
            # Use the version we already have.
            self.open_uis[node].show()
            return

        # Not cached. Generate the UI from the typename.
        ui = self.gen.generate_for_type(self.gs.data.type_of(node.rid))
        ui.setWindowTitle(f"Paragon - {node.name}")
        ui.setWindowIcon(QIcon("paragon.ico"))
        ui.set_target(node.rid)
        self.gs.data.mark_store_dirty(node.store)
        self.open_uis[node] = ui
        ui.show()

    def _on_multi_activated(self, index):
        # Prompt the user to select a file.
        data = self.gs.data
        multi = self.multis_list.model().data(index, QtCore.Qt.UserRole)
        keys = data.multi_keys(multi.id)
        choice, ok = QInputDialog.getItem(self, "Select File", "File", keys, -1)
        if not ok:
            return

        # Check if the UI was generated previously.
        key = (multi.id, choice)
        if key in self.open_uis:
            self.open_uis[key].show()
            return

        # Not cached. Open the file and generate a UI.
        rid = data.multi_open(multi.id, choice)
        ui = self.gen.generate_for_type(data.type_of(rid))
        ui.setWindowTitle(f"Paragon - {multi.name}")
        ui.setWindowIcon(QIcon("paragon.ico"))
        ui.set_target(rid)
        data.multi_mark_dirty(multi.id, choice)
        self.open_uis[key] = ui
        ui.show()