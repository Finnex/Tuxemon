# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2023 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from tuxemon.condition.condition import Condition
from tuxemon.db import OutputBattle
from tuxemon.locale import T
from tuxemon.technique.techeffect import TechEffect, TechEffectResult

if TYPE_CHECKING:
    from tuxemon.monster import Monster
    from tuxemon.technique.technique import Technique


class ForfeitEffectResult(TechEffectResult):
    pass


@dataclass
class ForfeitEffect(TechEffect):
    """
    Forfeit allows player to forfeit.

    """

    name = "forfeit"

    def apply(
        self, tech: Technique, user: Monster, target: Monster
    ) -> ForfeitEffectResult:
        combat = tech.combat_state
        assert combat
        player = self.session.player
        var = player.game_variables
        var["battle_last_result"] = OutputBattle.forfeit
        var["teleport_clinic"] = OutputBattle.lost
        combat._run = True
        extra = T.format(
            "combat_forfeit",
            {
                "npc": combat.players[1].name,
            },
        )
        # trigger forfeit
        for remove in combat.players:
            combat.clean_combat()
            del combat.monsters_in_play[remove]
            combat.players.remove(remove)
        # kill monsters -> teleport center
        for mon in player.monsters:
            faint = Condition()
            faint.load("faint")
            mon.current_hp = 0
            mon.status = [faint]

        return {
            "success": True,
            "damage": 0,
            "element_multiplier": 0.0,
            "should_tackle": False,
            "extra": extra,
        }
