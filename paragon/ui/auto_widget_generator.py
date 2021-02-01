from paragon.ui.controllers.auto.bitflags_widget import BitflagsWidget
from paragon.ui.controllers.auto.color_picker import ColorPicker
from paragon.ui.controllers.auto.icon_combo_box import IconComboBox
from paragon.ui.controllers.auto.labeled_spin_boxes import LabeledSpinBoxes
from paragon.ui.controllers.auto.list_widget import ListWidget

from paragon.ui.controllers.auto.check_box import CheckBox
from paragon.ui.controllers.auto.data_combo_box import DataComboBox
from paragon.ui.controllers.auto.float_spin_box import FloatSpinBox
from paragon.ui.controllers.auto.grid import Grid
from paragon.ui.controllers.auto.group_box import GroupBox
from paragon.ui.controllers.auto.hbox import HBox
from paragon.ui.controllers.auto.int_spin_box import IntSpinBox

from paragon.model.auto_generator_state import AutoGeneratorState
from paragon.model.auto_ui import (
    FormSpec,
    StringLineEditSpec,
    IntSpinBoxSpec,
    HexLineEditSpec,
    CheckBoxSpec,
    ListWidgetSpec,
    MessageWidgetSpec,
    ReferenceWidgetSpec,
    RecordWidgetSpec,
    FloatSpinBoxSpec,
    ScrollSpec,
)
from paragon.ui.controllers.auto.form import Form
from paragon.ui.controllers.auto.hex_line_edit import HexLineEdit
from paragon.ui.controllers.auto.label import Label
from paragon.ui.controllers.auto.message_widget import MessageWidget
from paragon.ui.controllers.auto.mini_portrait_box import MiniPortraitBox
from paragon.ui.controllers.auto.portrait_viewer import PortraitViewer
from paragon.ui.controllers.auto.record_widget import RecordWidget
from paragon.ui.controllers.auto.reference_widget import ReferenceWidget
from paragon.ui.controllers.auto.scroll import Scroll
from paragon.ui.controllers.auto.spin_box_matrix import SpinBoxMatrix
from paragon.ui.controllers.auto.spin_boxes import SpinBoxes
from paragon.ui.controllers.auto.string_line_edit import StringLineEdit
from paragon.ui.controllers.auto.tabs import Tabs
from paragon.ui.controllers.auto.vbox import VBox
from paragon.ui.controllers.auto.widget import Widget


class AutoWidgetGenerator:
    def __init__(self, ms, gs):
        self.ms = ms
        self.gs = gs
        self.data = gs.data
        self.specs = gs.specs

        self.defaults = {
            "top_level": ScrollSpec(type="scroll", inner=FormSpec(type="form")),
            "string": StringLineEditSpec(type="string_line_edit"),
            "label": StringLineEditSpec(type="string_line_edit"),
            "int": IntSpinBoxSpec(type="int_spin_box"),
            "float": FloatSpinBoxSpec(type="float_spin_box"),
            "bytes": HexLineEditSpec(type="hex_line_edit"),
            "bool": CheckBoxSpec(type="check_box"),
            "list": ListWidgetSpec(type="list_widget"),
            "message": MessageWidgetSpec(type="message_widget"),
            "reference": ReferenceWidgetSpec(type="reference_widget"),
            "record": RecordWidgetSpec(type="record_widget"),
        }

    def generate_for_type(self, typename):
        type_metadata = self.data.type_metadata(typename)
        field_metadata = self.data.field_metadata(typename)
        state = AutoGeneratorState(
            main_state=self.ms,
            game_state=self.gs,
            generator=self,
            type_metadata=type_metadata,
            field_metadata=field_metadata,
            typename=typename,
        )
        return self.generate_top_level(state, self.get_top_level_spec(typename))

    @staticmethod
    def generate_top_level(state, spec):
        if spec.type == "form":
            return Form(state, spec)
        elif spec.type == "widget":
            return Widget(state, spec)
        elif spec.type == "group_box":
            return GroupBox(state, spec)
        elif spec.type == "hbox":
            return HBox(state, spec)
        elif spec.type == "vbox":
            return VBox(state, spec)
        elif spec.type == "label":
            return Label(state, spec)
        elif spec.type == "scroll":
            return Scroll(state, spec)
        elif spec.type == "grid":
            return Grid(state, spec)
        elif spec.type == "tabs":
            return Tabs(state, spec)
        elif spec.type == "spin_box_matrix":
            return SpinBoxMatrix(state, spec)
        elif spec.type == "portrait_viewer":
            return PortraitViewer(state, spec)
        elif spec.type == "mini_portrait_box":
            return MiniPortraitBox(state, spec)
        else:
            raise NotImplementedError(f"Unsupported spec {spec.type}")

    def generate(self, state, field_id):
        fm = state.field_metadata[field_id]
        typename = state.typename
        spec = self.get_field_spec(typename, fm["id"], fm["type"])
        if spec.type == "string_line_edit":
            return StringLineEdit(state, field_id)
        elif spec.type == "hex_line_edit":
            return HexLineEdit(state, field_id)
        elif spec.type == "int_spin_box":
            return IntSpinBox(state, spec, field_id)
        elif spec.type == "float_spin_box":
            return FloatSpinBox(state, field_id)
        elif spec.type == "data_combo_box":
            return DataComboBox(state, spec, field_id)
        elif spec.type == "check_box":
            return CheckBox(state, field_id)
        elif spec.type == "list_widget":
            return ListWidget(state, field_id)
        elif spec.type == "reference_widget":
            return ReferenceWidget(state, field_id)
        elif spec.type == "message_widget":
            return MessageWidget(state, field_id)
        elif spec.type == "record_widget":
            return RecordWidget(state, spec, field_id)
        elif spec.type == "bitflags_widget":
            return BitflagsWidget(state, spec, field_id)
        elif spec.type == "spin_boxes":
            return SpinBoxes(state, field_id)
        elif spec.type == "labeled_spin_boxes":
            return LabeledSpinBoxes(state, spec, field_id)
        elif spec.type == "color_picker":
            return ColorPicker(state, field_id)
        elif spec.type == "icon_combo_box":
            return IconComboBox(state, spec, field_id)
        else:
            raise NotImplementedError(f"Unsupported spec {spec.type}")

    def get_top_level_spec(self, typename):
        if spec := self.specs.get_top_level_spec(typename):
            return spec
        else:
            return self.defaults["top_level"]

    def get_field_spec(self, typename, field_id, field_type):
        if spec := self.specs.get_field_spec(typename, field_id):
            return spec
        else:
            return self.defaults[field_type]