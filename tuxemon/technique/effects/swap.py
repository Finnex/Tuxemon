# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2023 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
from __future__ import annotations

from dataclasses import dataclass
from functools import partial
from typing import TYPE_CHECKING

from tuxemon.technique.techeffect import TechEffect, TechEffectResult

if TYPE_CHECKING:
    from tuxemon.monster import Monster
    from tuxemon.technique.technique import Technique


class SwapEffectResult(TechEffectResult):
    pass


@dataclass
class SwapEffect(TechEffect):
    """
    Used just for combat: change order of monsters.

    Position of monster in party will be changed.

    Returns:
        Dict summarizing the result.

    """

    name = "swap"

    def apply(
        self, tech: Technique, user: Monster, target: Monster
    ) -> SwapEffectResult:
        # TODO: implement actions as events, so that combat state can find them
        # TODO: relies on setting "combat_state" attribute.  maybe clear it up
        # later
        # TODO: these values are set in combat_menus.py
        player = self.session.player
        assert tech.combat_state
        # TODO: find a way to pass values. this will only work for SP games with one monster party
        combat_state = tech.combat_state

        def swap_add(removed: Monster) -> None:
            # TODO: make accommodations for battlefield positions
            combat_state.add_monster_into_play(player, target, removed)

        # get the original monster to be swapped out
        original_monster = combat_state.monsters_in_play[player][0]

        # rewrite actions to target the new monster.  must be done before original is removed
        combat_state.rewrite_action_queue_target(original_monster, target)

        # remove the old monster and all their actions
        combat_state.remove_monster_from_play(original_monster)

        # give a slight delay
        combat_state.task(partial(swap_add, original_monster), 0.75)

        return {
            "success": True,
            "damage": 0,
            "element_multiplier": 0.0,
            "should_tackle": False,
            "extra": None,
        }
