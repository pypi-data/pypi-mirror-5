#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#   Copyright 2010-2013 Tuukka Turto
#
#   This file is part of pyherc.
#
#   pyherc is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   pyherc is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with pyherc.  If not, see <http://www.gnu.org/licenses/>.

"""
module for configuring player characters
"""
from pyherc.generators import CreatureConfiguration, InventoryConfiguration

def init_players(context):
    """
    Initialise creatures

    :returns: list of creature configurations
    :rtype: [CreatureConfiguration]
    """
    config = []
    surface_manager = context.surface_manager

    config.append(CreatureConfiguration(name = 'Adventurer',
                                        body = 6,
                                        finesse = 7,
                                        mind = 8,
                                        hp = 9,
                                        speed = 2.5,
                                        icons = surface_manager.add_icon('adventurer', ':strong-2.png', '@', ['white', 'bold']),
                                        attack = 1,
                                        ai = None,
                                        effect_handles = None,
                                        inventory = [InventoryConfiguration(
                                                            item_name = 'sword',
                                                            min_amount = 1,
                                                            max_amount = 1,
                                                            probability = 100),
                                                     InventoryConfiguration(
                                                            item_name = 'leather armour',
                                                            min_amount = 1,
                                                            max_amount = 1,
                                                            probability = 100),
                                                     InventoryConfiguration(
                                                            item_name = 'bow',
                                                            min_amount = 1,
                                                            max_amount = 1,
                                                            probability = 100),
                                                     InventoryConfiguration(
                                                            item_name = 'arrow',
                                                            min_amount = 1,
                                                            max_amount = 1,
                                                            probability = 100),
                                                     InventoryConfiguration(
                                                            item_name = 'war arrow',
                                                            min_amount = 1,
                                                            max_amount = 1,
                                                            probability = 100),
                                                     InventoryConfiguration(
                                                            item_name = 'blunt arrow',
                                                            min_amount = 1,
                                                            max_amount = 1,
                                                            probability = 100),
                                                     InventoryConfiguration(
                                                            item_name = 'healing potion',
                                                            min_amount = 1,
                                                            max_amount = 2,
                                                            probability = 50)],
                                        description = '\n'.join(['A skillful adventurer.',
                                                                '',
                                                                'Adventurer is armed and ready to explore any dungeon he sees. He is strong enough to survive combat with some of the dangers, while some he definitely should avoid',
                                                                'Adventurer also carries some potions that will help him on his journey.'])))

    config.append(CreatureConfiguration(name = 'Warrior',
                                        body = 8,
                                        finesse = 7,
                                        mind = 6,
                                        hp = 12,
                                        speed = 2.5,
                                        icons = surface_manager.add_icon('warrior', ':strong-2.png', '@', ['white', 'bold']),
                                        attack = 2,
                                        ai = None,
                                        effect_handles = None,
                                        inventory = [InventoryConfiguration(
                                                            item_name = 'sword',
                                                            min_amount = 1,
                                                            max_amount = 1,
                                                            probability = 100),
                                                     InventoryConfiguration(
                                                            item_name = 'warhammer',
                                                            min_amount = 1,
                                                            max_amount = 1,
                                                            probability = 100),
                                                     InventoryConfiguration(
                                                            item_name = 'scale mail',
                                                            min_amount = 1,
                                                            max_amount = 1,
                                                            probability = 100),
                                                     InventoryConfiguration(
                                                            item_name = 'dagger',
                                                            min_amount = 1,
                                                            max_amount = 1,
                                                            probability = 100)],
                                        description = '\n'.join(['A stout warrior',
                                                                '',
                                                                'Warrior is armed to teeth and tends to solve his problems with brute force.',
                                                                'Warrior has nice selection of weapons to use but very little of anything else.'])))

    return config
