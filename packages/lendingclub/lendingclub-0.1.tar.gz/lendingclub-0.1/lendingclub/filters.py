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
import json
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
            self.__merge_values(filters, self)

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
        return dict.__getitem__(self, key)

    def __setitem__(self, key, value):

        # If setting grades, merge dictionary instead of replace
        if key == 'grades' and self.__initialized is True:
            assert type(value) is dict, 'The grades filter must be a dictionary object'
            self.__merge_values(value, dict.__getitem__(self, 'grades'))
            value = self['grades']

        # Set value and normalize
        dict.__setitem__(self, key, value)
        self.__normalize()

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

        # Map the loan value keys to the filter keys
        req = {
            'loan_id': None,
            'loanGrade': 'grade',
            'loanLength': 'term',
            'loanUnfundedAmount': 'progress',
            'loanAmountRequested': 'progress',
            'alreadyInvestedIn': 'exclude_existing',
            'purpose': 'loan_purpose',
        }

        # Throw an error if the loan does not contain one of the criteria keys that this filter has
        for key, criteria in req.iteritems():
            if criteria in self and key not in loan:
                raise FilterValidationError('Loan does not have a "{0}" value.'.format(key), loan, criteria)

        # Grade
        grade = loan['loanGrade'][0]  # Extract the letter portion of the loan
        if 'grades' in self and self['grades']['All'] is not True:
            if grade not in self['grades']:
                raise FilterValidationError('Loan grade "{0}" is unknown'.format(grade), loan, 'grade')
            elif self['grades'][grade] is False:
                raise FilterValidationError(loan=loan, criteria='grade')

        # Term
        if 'term' in self:
            if loan['loanLength'] == 36 and self['term']['Year3'] is False:
                raise FilterValidationError(loan=loan, criteria='loan term')
            elif loan['loanLength'] == 60 and self['term']['Year5'] is False:
                raise FilterValidationError(loan=loan, criteria='loan term')

        # Progress
        if 'funding_progress' in self:
            loan_progress = (1 - (loan['loanUnfundedAmount'] / loan['loanAmountRequested'])) * 100
            if self['funding_progress'] > loan_progress:
                raise FilterValidationError(loan=loan, criteria='funding progress')

        # Exclude existing
        if 'exclude_existing' in self:
            if self['exclude_existing'] is True and loan['alreadyInvestedIn'] is True:
                raise FilterValidationError(loan=loan, criteria='exclude loans you are invested in')

        # Loan purpose (either an array or single value)
        if 'loan_purpose' in self and loan['purpose'] is not False:
            purpose = self['loan_purpose']
            if type(purpose) is not dict:
                purpose = {purpose: True}

            if 'All' not in purpose or purpose['All'] is False:
                if loan['purpose'] not in purpose:
                    raise FilterValidationError(loan=loan, criteria='loan purpose')

        return True

    def search_string(self):
        """"
        Returns the JSON string that LendingClub expects for it's search
        """
        self.__normalize()

        # Get the template
        tmpl_source = unicode(open(self.tmpl_file).read())

        # Process template
        compiler = Compiler()
        template = compiler.compile(tmpl_source)
        out = template(self)
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
    id = None
    lc = None
    name = None
    json = None
    json_text = None
    response = None

    @staticmethod
    def all_filters(lc):
        """
        Get a list of all your saved filters

        Parameters:
            lc -- An instance of the LendingClub class

        Returns a list of SavedFilter objects
        """

        filters = []
        response = lc.session.get('/browse/getSavedFiltersAj.action')
        json_response = response.json()

        # Load all filters
        if lc.session.json_success(json_response):
            for saved in json_response['filters']:
                filters.append(SavedFilter(lc, saved['id']))

        return filters

    def __init__(self, lc, filter_id):
        """
        Load the filter by ID or Name

        Parameters:
            lc -- An instance of the LendingClub class
            filter_id -- The ID of the filter to load (find it by calling `all_filters()`)
        """

        self.id = filter_id
        self.lc = lc
        self.load()

    def reload(self):
        """
        Reload the saved filter
        """
        self.load()

    def load(self):
        """
        Load the filter from the server
        """

        # Attempt to load the saved filter
        payload = {
            'id': self.id
        }
        response = self.lc.session.get('/browse/getSavedFilterAj.action', query=payload)
        self.response = response
        json_response = response.json()

        if self.lc.session.json_success(json_response):
            self.name = json_response['filterName']

            #
            # Parse out the filter JSON string manually from the response JSON.
            # If the filter JSON is modified at all, or any value is out of order,
            # LendingClub will reject the filter and perform a wildcard search instead,
            # without any error. So we need to retain the filter JSON value exactly how it is given to us.
            #
            text = response.text

            # Cut off everything  before "filter": [...]
            text = re.sub('\n', '', text)
            text = re.sub('^.*?,\s*["\']filter["\']:\s*\[(.*)', '[\\1', text)

            # Now loop through the string until we find the end of the filter block
            # This is a simple parser that keeps track of block elements, quotes and
            # escape characters
            blockTracker = []
            blockChars = {
                '[': ']',
                '{': '}'
            }
            inQuote = False
            lastChar = None
            json_text = ""
            for char in text:
                json_text += char

                # Escape char
                if char == '\\':
                    if lastChar == '\\':
                        lastChar = ''
                    else:
                        lastChar = char
                    continue

                # Quotes
                if char == "'" or char == '"':
                    if inQuote is False:  # Starting a quote block
                        inQuote = char
                    elif inQuote == char:  # Ending a quote block
                        inQuote = False
                    lastChar = char
                    continue

                # Start of a block
                if char in blockChars.keys():
                    blockTracker.insert(0, blockChars[char])

                # End of a block, remove from block path
                elif len(blockTracker) > 0 and char == blockTracker[0]:
                    blockTracker.pop(0)

                # No more blocks in the tracker which means we're at the end of the filter block
                if len(blockTracker) == 0 and lastChar is not None:
                    break

                lastChar = char

            # Verify valid JSON
            try:
                json_test = json.loads(json_text)

                # Make sure it looks right
                assert type(json_test) is list, 'Expecting a list, instead received a {0}'.format(type(json_test))
                assert 'm_id' in json_test[0], 'Expecting a \'m_id\' property in each filter'
                assert 'm_value' in json_test[0], 'Expecting a \'m_value\' property in each filter'

                self.json = json_test
            except Exception as e:
                raise SavedFilterError('Could not parse filter from the JSON response: {0}'.format(str(e)))

            self.json_text = json_text
            self.analyze()

        else:
            raise SavedFilterError('A saved filter could not be found for ID {0}'.format(self.id), response)

    def __str__(self):
        return '<SavedFilter: {0}, \'{1}\'>'.format(self.id, self.name)

    def __repr__(self):
        return self.__str__()

    def __setitem__(self, key, value):
        raise SavedFilterError('A saved filter cannot be modified')

    def analyze(self):
        """
        Analyze the filter JSON and attempt to parse out the individual filters.
        """
        filter_values = {}

        # ID to filter name mapping
        name_map = {
            10: 'grades',
            11: 'loan_purpose',
            13: 'approved',
            15: 'funding_progress',
            38: 'exclude_existing',
            39: 'term',
            43: 'keyword'
        }

        if self.json is not None:
            filters = self.json

            for f in filters:
                if 'm_id' in f:
                    name = f['m_id']

                    # Get the name to represent this filter
                    if f['m_id'] in name_map:
                        name = name_map[f['m_id']]

                    # Get values
                    if 'm_value' in f:
                        raw_values = f['m_value']
                        value = {}

                        # Loop through multiple values
                        if type(raw_values) is list:

                            # A single non string value, is THE value
                            if len(raw_values) == 1 and type(raw_values[0]['value']) not in [str, unicode]:
                                value = raw_values[0]['value']

                            # Create a dict of values: name = True
                            for val in raw_values:
                                if type(val['value']) in [str, unicode]:
                                    value[val['value']] = True

                        # A single value
                        else:
                            value = raw_values

                        # Normalize grades array
                        if name == 'grades':
                            if 'All' not in value:
                                value['All'] = False

                    # Add filter value
                    filter_values[name] = value
                    dict.__setitem__(self, name, value)

        return filter_values

    def __normalize():
        pass

    def search_string(self):
        return self.json_text


class FilterByLoanID(Filter):
    """
    Creates a filter by loan ID or a string of comma delimited loan IDs
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
    request = None

    def __init__(self, value, request=None):
        self.value = value
        self.request = request

    def __str__(self):
        return repr(self.value)