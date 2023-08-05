# Copyright (c) 2013, The MITRE Corporation. All rights reserved.
# See LICENSE.txt for complete terms.

import cybox
import cybox.bindings.cybox_common as common_binding

class StructuredText(cybox.Entity):
    _binding = common_binding

    def __init__(self, value=None):
        self.value = value
        self.structuring_format = None

    def to_obj(self, structured_text_obj = None):
        if not structured_text_obj:
            text_obj = common_binding.StructuredTextType()
        else:
            text_obj = structured_text_obj

        text_obj.set_valueOf_(self.value)
        if self.structuring_format is not None:
            text_obj.set_structuring_format(self.structuring_format)
        return text_obj

    def to_dict(self):
        # Return a plain string if there is no format specified.
        if self.structuring_format is None:
            return self.value

        text_dict = {}
        text_dict['value'] = self.value
        text_dict['structuring_format'] = self.structuring_format

        return text_dict

    @classmethod
    def from_obj(cls, text_obj, text_class = None):
        if not text_obj:
            return None
        if not text_class:
            text = StructuredText()
        else:
            text = text_class

        text.value = text_obj.get_valueOf_()
        text.structuring_format = text_obj.get_structuring_format()

        return text

    @classmethod
    def from_dict(cls, text_dict, text_class = None):
        if text_dict is None:
            return None
        if not text_class:
            text = StructuredText()
        else:
            text = text_class

        if not isinstance(text_dict, dict):
            text.value = text_dict
        else:
            text.value = text_dict.get('value')
            text.structuring_format = text_dict.get('structuring_format')

        return text

