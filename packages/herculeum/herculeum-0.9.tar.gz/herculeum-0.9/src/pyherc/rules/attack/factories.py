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
Attack related factories are defined here
"""
from pyherc.aspects import logged
from pyherc.rules.attack.action import AttackAction, AdditionalRules
from pyherc.rules.attack.unarmed import UnarmedToHit
from pyherc.rules.attack.unarmed import UnarmedDamage
from pyherc.rules.attack.melee import MeleeToHit
from pyherc.rules.attack.melee import MeleeDamage
from pyherc.rules.factory import SubActionFactory

class AttackFactory(SubActionFactory):
    """
    Factory for constructing attack actions
    """

    @logged
    def __init__(self, factories):
        """
        Constructor for this factory
        """
        super(AttackFactory, self).__init__()
        self.action_type = 'attack'

        if hasattr(factories, '__iter__'):
            self.factories = factories
        else:
            self.factories = []
            self.factories.append(factories)


class UnarmedCombatFactory():
    """
    Factory for producing unarmed combat actions
    """
    @logged
    def __init__(self, effect_factory, dying_rules):
        """
        Constructor for this factory
        """
        self.attack_type = 'unarmed'
        self.effect_factory = effect_factory
        self.dying_rules = dying_rules

    def __str__(self):
        return 'unarmed combat factory'

    @logged
    def can_handle(self, parameters):
        """
        Can this factory process these parameters

        :param parameters: parameters to check
        :type parameters: UnarmedAttackParameters
        :returns: true if factory is capable of handling parameters
        :rtype: boolean
        """
        return self.attack_type == parameters.attack_type

    @logged
    def get_action(self, parameters):
        """
        Create a attack action

        :param parameters: parameters used to control attack creation
        :type parameters: UnarmedAttackParameters
        :returns: action that can be executed
        :rtype: AttackAction
        """
        attacker = parameters.attacker
        target = self.get_target(parameters)
        damage = [(attacker.get_attack(), 'crushing')]

        attack = AttackAction('unarmed',
                    to_hit = UnarmedToHit(attacker, target,
                                          parameters.random_number_generator),
                    damage = UnarmedDamage(damage = damage),
                    attacker = attacker,
                    target = target,
                    effect_factory = self.effect_factory,
                    dying_rules = self.dying_rules,
                    additional_rules = AdditionalRules(attacker))

        return attack

    @logged
    def get_target(self, parameters):
        """
        Get target of the attack

        :param parameters: attack parameters
        :type parameters: UnarmedAttackParameters
        :returns: target character if found, otherwise None
        :rtype: Character
        """
        attacker = parameters.attacker
        location = attacker.location
        direction = parameters.direction
        level = attacker.level

        if direction == 1:
            target_location = (location[0], location[1] - 1)
        elif direction == 2:
            target_location = (location[0] + 1, location[1] - 1)
        elif direction == 3:
            target_location = (location[0] + 1, location[1])
        elif direction == 4:
            target_location = (location[0] + 1, location[1] + 1)
        elif direction == 5:
            target_location = (location[0], location[1] + 1)
        elif direction == 6:
            target_location = (location[0] - 1, location[1] + 1)
        elif direction == 7:
            target_location = (location[0] - 1, location[1])
        elif direction == 8:
            target_location = (location[0] - 1, location[1] - 1)
        else:
            target_location = None

        if target_location != None:
            target = level.get_creature_at(target_location)
            return target
        else:
            return None

class MeleeCombatFactory():
    """
    Factory for producing melee combat actions
    """
    @logged
    def __init__(self, effect_factory, dying_rules):
        """
        Constructor for this factory
        """
        self.attack_type = 'melee'
        self.effect_factory = effect_factory
        self.dying_rules = dying_rules

    def __str__(self):
        return 'melee combat factory'

    @logged
    def can_handle(self, parameters):
        """
        Can this factory process these parameters

        :param parameters: parameters to check
        :type parameters: MeleeAttackParameters
        :returns: true if factory is capable of handling parameters
        :rtype: boolean
        """
        return self.attack_type == parameters.attack_type

    @logged
    def get_action(self, parameters):
        """
        Create a attack action

        :param parameters: parameters used to control attack creation
        :type parameters: MeleeAttackParameters
        :returns: action that can be executed
        :rtype: AttackAction
        """
        attacker = parameters.attacker
        target = self.get_target(parameters)
        weapon = attacker.inventory.weapon
        weapon_data = weapon.weapon_data

        attack = AttackAction(
                    attack_type = 'melee',
                    to_hit = MeleeToHit(attacker, target,
                                        parameters.random_number_generator),
                    damage = MeleeDamage(damage = weapon_data.damage),
                    attacker = attacker,
                    target = target,
                    effect_factory = self.effect_factory,
                    dying_rules = self.dying_rules,
                    additional_rules = AdditionalRules(attacker))

        return attack

    @logged
    def get_target(self, parameters):
        """
        Get target of the attack

        :param parameters: parameters to control attack
        :type parameters: MeleeAttackParameters
        :returns: target character if found, otherwise None
        :rtype: Character
        """
        attacker = parameters.attacker
        location = attacker.location
        direction = parameters.direction
        level = attacker.level

        if direction == 1:
            target_location = (location[0], location[1] - 1)
        elif direction == 2:
            target_location = (location[0] + 1, location[1] - 1)
        elif direction == 3:
            target_location = (location[0] + 1, location[1])
        elif direction == 4:
            target_location = (location[0] + 1, location[1] + 1)
        elif direction == 5:
            target_location = (location[0], location[1] + 1)
        elif direction == 6:
            target_location = (location[0] - 1, location[1] + 1)
        elif direction == 7:
            target_location = (location[0] - 1, location[1])
        elif direction == 8:
            target_location = (location[0] - 1, location[1] - 1)
        else:
            target_location = None

        target = level.get_creature_at(target_location)

        if target_location != None:
            target = level.get_creature_at(target_location)
            return target
        else:
            return None
