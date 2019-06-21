#!/usr/bin/env python3
"""
Copyright 2019 Marco Lattuada

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import logging
import random

import model_building.design_space as ds
import model_building.experiment_configuration as ec

class GeneratorsFactory:
    """
    Factory calls to build the logical hierarchy of generators

    Attributes
    ----------
    _campaign_configuration: dict of dict
        The set of options specified by the user though command line and campaign configuration files

    Methods
    -------
    build()
        Build the required hierarchy of generators on the basis of the configuration file
    """

    _campaign_configuration = None

    _random_generator = random.Random(0)

    _logger = None

    def __init__(self, campaign_configuration, seed):
        """
        Parameters
        ----------
        campaign_configuration: #TODO: add type
            The set of options specified by the user though command line and campaign configuration files

        seed: integer
            The seed to be used in random based activities

        Returns
        -------
        ExpConfsGenerator
            The top level ExpConfsGenerator to be used to generate all the experiment configurations
        """
        self._campaign_configuration = campaign_configuration
        self._random_generator = random.Random(seed)
        self._logger = logging.getLogger(__name__)

    def build(self):
        """
        Build the required hierarchy of generators on the basis of the configuration file

        The methods start from the leaves and go up. Intermediate wrappers must be added or not on the basis of the requirements of the campaign configuration
        """
        string_techique_to_enum = {v: k for k, v in ec.enum_to_configuration_label.items()}

        generators = {}

        for technique in self._campaign_configuration['General']['techniques']:
            self._logger.debug("Building technique generator for %s", technique)
            generators[technique] = ds.TechniqueExpConfsGenerator(self._campaign_configuration, None, string_techique_to_enum[technique])
        assert generators

        #TODO: if we want to use k-fold, wraps the generator with KFoldExpConfsGenerator

        #TODO: if we want to use feature selection, wraps with a subclass of FSExpConfsGenerator

        multitechniques_generator = ds.MultiTechniquesExpConfsGenerator(self._campaign_configuration, self._random_generator.random(), generators)

        top_generator = ds.RepeatedExpConfsGenerator(self._campaign_configuration, self._random_generator.random(), self._campaign_configuration['General']['run_num'], multitechniques_generator)
        return top_generator
