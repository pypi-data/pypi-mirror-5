#!/usr/bin/env python

"""
Create a search filter
"""

"""
The MIT License (MIT)

Copyright (c) 2013 Jeremy Gillick

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import os
import re
from pybars import Compiler


class Filter(dict):

    tmpl_file = False
    __initialized = False
    __normalizing = False

    def __init__(self, filters=None):
        """
        Set the default search filter values
        """

        # Set filter values
        self['max_per_note'] = 0    # The most you most you want to invest per note, or 0 for no limit
        self['term'] = {
            'Year3': True,
            'Year5': True
        }
        self['exclude_existing'] = True
        self['funding_progress'] = 0
        self['grades'] = {
            'All': True,
            'A': False,
            'B': False,
            'C': False,
            'D': False,
            'E': False,
            'F': False,
            'G': False
        }

        # Merge in filter values
        if filters is not None:
            self.__merge_values(filters, self.__dict__)

        # Set the template file path
        this_path = os.path.dirname(os.path.realpath(__file__))
        self.tmpl_file = os.path.join(this_path, 'filter.handlebars')

        self.__initialized = True
        self.__normalize()

    def __merge_values(self, from_dict, to_dict):
        """
        Merge dictionary objects recursively, by only updating keys existing in to_dict
        """
        for key, value in from_dict.iteritems():

            # Only if the key already exists
            if key in to_dict:

                # Make sure the values are the same datatype
                assert type(to_dict[key]) is type(from_dict[key]), 'Data type for {0} is incorrect: {1}, should be {2}'.format(key, type(from_dict[key]), type(to_dict[key]))

                # Recursively dive into the next dictionary
                if type(to_dict[key]) is dict:
                    to_dict[key] = self.__merge_values(from_dict[key], to_dict[key])

                # Replace value
                else:
                    to_dict[key] = from_dict[key]

        return to_dict

    def __getitem__(self, key):
        self.__normalize()
        return self.__dict__[key]

    def __setitem__(self, key, value):

        # If setting grades, merge dictionary instead of replace
        if key == 'grades' and self.__initialized is True:
            assert type(value) is dict, 'The grades filter must be a dictionary object'
            self.__merge_values(value, self.__dict__['grades'])
            value = self.__dict__['grades']

        # Set value and normalize
        self.__dict__[key] = value
        self.__normalize()

    def __repr__(self):
        return repr(self.__dict__)

    def __str__(self):
        return repr(self.__dict__)

    def __normalize_grades(self):
        """
        Adjust the grades list.
        If a grade has been set, set All to false
        """

        if self['grades']['All'] is True:
            for grade in self['grades']:
                if grade != 'All' and self['grades'][grade] is True:
                    self['grades']['All'] = False
                    break

    def __normalize_progress(self):
        """
        Adjust the funding progress filter to be a factor of 10
        """

        progress = self['funding_progress']
        if progress % 10 != 0:
            progress = round(float(progress) / 10)
            progress = int(progress) * 10

            self['funding_progress'] = progress

    def __normalize(self):
        """
        Adjusts the values of the filters to be correct.
        For example, if you set grade 'B' to True, then 'All'
        should be set to False
        """

        # Don't normalize if we're already normalizing or intializing
        if self.__normalizing is True or self.__initialized is False:
            return

        self.__normalizing = True
        self.__normalize_grades()
        self.__normalize_progress()
        self.__normalizing = False

    def validate(self, results):
        """
        Validate that the results indeed match the filters.
        It's a VERY good idea to run your search results through this, even though
        the filters were passed to LendingClub in your search. Since we're not using formal
        APIs for LendingClub, they could change the way their search works at anytime, which
        might break the filters.

        Parameters:
            results -- A list of loan note records returned from LendingClub

        Returns True or raises FilterValidationError
        """
        for loan in results:
            self.validate_one(loan)

        return True

    def validate_one(self, loan):
        """
        Validate a single result record to the filters

        Parameters:
            loan -- A single loan note record returned from LendingClub

        Returns True or raises FilterValidationError
        """
        assert type(loan) is dict, 'loan parameter must be a dictionary object'

        # Check required keys for a loan
        req = {
            'loan_id': None,
            'loanGrade': 'grade',
            'loanLength': 'term',
            'loanUnfundedAmount': 'progress',
            'loanAmountRequested': 'progress',
            'alreadyInvestedIn': 'exclude_existing'
        }
        for key, criteria in req.iteritems():
            if key not in loan:
                raise FilterValidationError('Loan does not have a "{0}" value.'.format(key), loan, criteria)

        # Grade
        grade = loan['loanGrade'][0]  # Extract the letter portion of the loan
        if self.grades['All'] is not True:
            if grade not in self.grades:
                raise FilterValidationError('Loan grade "{0}" is unknown'.filter(grade), loan, 'grade')
            elif self.grades[grade] is False:
                raise FilterValidationError(loan=loan, criteria='grade')

        # Term
        if loan['loanLength'] == 36 and self['term']['Year3'] is False:
            raise FilterValidationError(loan=loan, criteria='term')
        elif loan['loanLength'] == 60 and self['term']['Year5'] is False:
            raise FilterValidationError(loan=loan, criteria='term')

        # Progress
        loan_progress = (1 - (loan['loanUnfundedAmount'] / loan['loanAmountRequested'])) * 100
        if self['funding_progress'] > loan_progress:
            raise FilterValidationError(loan=loan, criteria='funding_progress')

        # Exclude existing
        if self['exclude_existing'] is True and loan['alreadyInvestedIn'] is True:
            raise FilterValidationError(loan=loan, criteria='alreadyInvestedIn')

        return True

    def search_string(self):
        """"
        Returns the JSON string that LendingClub expects for it's search
        """

        # Get the template
        tmpl_source = unicode(open(self.tmpl_file).read())

        # Process template
        compiler = Compiler()
        template = compiler.compile(tmpl_source)
        out = template(self.__dict__)
        if not out:
            return False
        out = ''.join(out)

        #
        # Cleanup output and remove all extra space
        #

        # remove extra spaces
        out = re.sub('\n', '', out)
        out = re.sub('\s{3,}', ' ', out)

        # Remove hanging commas i.e: [1, 2,]
        out = re.sub(',\s*([}\\]])', '\\1', out)

        # Space between brackets i.e: ],  [
        out = re.sub('([{\\[}\\]])(,?)\s*([{\\[}\\]])', '\\1\\2\\3', out)

        # Cleanup spaces around [, {, }, ], : and , characters
        out = re.sub('\s*([{\\[\\]}:,])\s*', '\\1', out)

        return out


class SavedFilter(Filter):
    """
    Instead of building a filter, pull a filter you have created and
    saved on LendingClub.

    This kind of filter cannot be inspected or changed.
    """
    filter_id = None
    name = None
    json = None

    def __init__(self, filter_id):
        """
        Load the filter by ID
        """
        pass

    def __setitem__(self, key, value):
        raise SavedFilterError('A saved filter cannot be modified')

    def __normalize():
        pass

    def validate(self, results):
        return True

    def validate_one(self, loan):
        return True

    def search_string(self):
        return self.json


class FilterByID(Filter):
    """
    Creates a filter by loan_id
    """

    def __init__(self, loan_id):
        self['loan_id'] = loan_id
        this_path = os.path.dirname(os.path.realpath(__file__))
        self.tmpl_file = os.path.join(this_path, 'filter.handlebars')

    def validate(self, results):
        return True

    def validate_one(self, loan):
        return True

    def __normalize():
        pass


class FilterValidationError(Exception):
    """
    A loan note does not match the filters set.

    Attributes:
        value -- The error message
        loan -- The loan note that did not match
        criteria -- The filter that did not match.
    """
    value = None
    loan = None
    criteria = None

    def __init__(self, value=None, loan=None, criteria=None):
        self.loan = loan
        self.criteria = criteria

        if value is None:
            if criteria is None:
                self.value = 'Did not meet filter criteria'
            else:
                self.value = 'Did not meet filter criteria for {0}'.format(criteria)
        else:
            self.value = value

    def __str__(self):
        return repr(self.value)


class SavedFilterError(Exception):
    value = None

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)