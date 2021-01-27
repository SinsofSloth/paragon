import dataclasses

from paragon.core.services.icons import Icons
from paragon.model.project import Project
from paragon import paragon as paragon_core
from paragon.ui.enum_loader import EnumLoader
from paragon.ui.models import Models
from paragon.ui.specs import Specs


@dataclasses.dataclass
class FE14State:
    project: Project
    data: paragon_core.GameData
    specs: Specs
    models: Models
    enums: EnumLoader
    icons: Icons
