# Copyright 2012-2013 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
import logging
from six.moves import cStringIO
from bcdoc.docstringparser import DocStringParser
from bcdoc.style import ReSTStyle
from bcdoc.clidocevents import DOC_EVENTS

SCALARS = ('string', 'integer', 'boolean', 'timestamp', 'float', 'double')
LOG = logging.getLogger(__name__)


class ReSTDocument(object):

    def __init__(self, fp=None, target='man'):
        if fp is None:
            fp = cStringIO()
        self.fp = fp
        self.style = ReSTStyle(self)
        self.target = target
        self.parser = DocStringParser(self)
        self.keep_data = True
        self.do_translation = False
        self.translation_map = {}

    def write(self, s):
        if self.keep_data:
            self.fp.write(s)

    def writeln(self, s):
        if self.keep_data:
            self.fp.write('%s%s\n' % (self.style.spaces(), s))

    def writeraw(self, s):
        if self.keep_data:
            self.fp.write(s)

    def translate_words(self, words):
        return [self.translation_map.get(w, w) for w in words]

    def handle_data(self, data):
        if data and self.keep_data:
            # Some of the JSON service descriptions have
            # Unicode constants embedded in the doc strings
            # which cause UnicodeEncodeErrors in Python 2.x
            try:
                self.write(data)
            except UnicodeEncodeError:
                self.write(data.encode('utf-8'))

    def include_doc_string(self, doc_string):
        if doc_string:
            self.parser.feed(doc_string)


class CLIDocumentEventHandler(object):

    def __init__(self, help_command):
        self.help_command = help_command
        self.register(help_command.session, help_command.event_class)
        self.help_command.doc.translation_map = self.build_translation_map()

    def build_translation_map(self):
        return dict()

    def _map_handlers(self, session, event_class, mapfn):
        for event in DOC_EVENTS:
            event_handler_name = event.replace('-', '_')
            if hasattr(self, event_handler_name):
                event_handler = getattr(self, event_handler_name)
                format_string = DOC_EVENTS[event]
                num_args = len(format_string.split('.')) - 2
                format_args = (event_class,) + ('*',) * num_args
                event_string = event + format_string % format_args
                unique_id = event_class + event_handler_name
                mapfn(event_string, event_handler, unique_id)

    def register(self, session, event_class):
        """
        The default register iterates through all of the
        available document events and looks for a corresponding
        handler method defined in the object.  If it's there, that
        handler method will be registered for the all events of
        that type for the specified ``event_class``.
        """
        self._map_handlers(session, event_class, session.register)

    def unregister(self):
        """
        The default unregister iterates through all of the
        available document events and looks for a corresponding
        handler method defined in the object.  If it's there, that
        handler method will be unregistered for the all events of
        that type for the specified ``event_class``.
        """
        self._map_handlers(self.help_command.session,
                           self.help_command.event_class,
                           self.help_command.session.unregister)


class ProviderDocumentEventHandler(CLIDocumentEventHandler):

    def doc_title(self, help_command, **kwargs):
        doc = help_command.doc
        doc.style.h1(help_command.name)

    def doc_description(self, help_command, **kwargs):
        doc = help_command.doc
        doc.style.h2('Description')
        doc.include_doc_string(help_command.description)
        doc.style.new_paragraph()

    def doc_synopsis_start(self, help_command, **kwargs):
        doc = help_command.doc
        doc.style.h2('Synopsis')
        doc.style.codeblock(help_command.synopsis)
        doc.include_doc_string(help_command.help_usage)

    def doc_synopsis_end(self, help_command, **kwargs):
        doc = help_command.doc
        doc.style.new_paragraph()

    def doc_options_start(self, help_command, **kwargs):
        doc = help_command.doc
        doc.style.h2('Options')

    def doc_option(self, arg_name, help_command, **kwargs):
        doc = help_command.doc
        argument = help_command.arg_table[arg_name]
        doc.writeln('``%s`` (%s)' % (argument.cli_name,
                                     argument.cli_type_name))
        doc.include_doc_string(argument.documentation)
        if argument.choices:
            doc.style.start_ul()
            for choice in argument.choices:
                doc.style.li(choice)
            doc.style.end_ul()

    def doc_subitems_start(self, help_command, **kwargs):
        doc = help_command.doc
        doc.style.h2('Available Services')
        doc.style.toctree()

    def doc_subitem(self, command_name, help_command, **kwargs):
        doc = help_command.doc
        file_name = '%s/index' % command_name
        doc.style.tocitem(command_name, file_name=file_name)


class ServiceDocumentEventHandler(CLIDocumentEventHandler):

    def build_translation_map(self):
        d = {}
        for op in self.help_command.obj.operations:
            d[op.name] = op.cli_name
        return d

    def doc_title(self, help_command, **kwargs):
        doc = help_command.doc
        doc.style.h1(help_command.name)

    def doc_description(self, help_command, **kwargs):
        doc = help_command.doc
        service = help_command.obj
        doc.style.h2('Description')
        doc.include_doc_string(service.documentation)

    def doc_subitems_start(self, help_command, **kwargs):
        doc = help_command.doc
        doc.style.h2('Available Commands')
        doc.style.toctree()

    def doc_subitem(self, command_name, help_command, **kwargs):
        doc = help_command.doc
        doc.style.tocitem(command_name)


class OperationDocumentEventHandler(CLIDocumentEventHandler):

    def build_translation_map(self):
        LOG.debug('build_translation_map')
        operation = self.help_command.obj
        d = {}
        for param in operation.params:
            d[param.name] = param.cli_name
        for operation in operation.service.operations:
            d[operation.name] = operation.cli_name
        return d

    def doc_title(self, help_command, **kwargs):
        doc = help_command.doc
        doc.style.h1(help_command.name)

    def doc_description(self, help_command, **kwargs):
        doc = help_command.doc
        operation = help_command.obj
        doc.style.h2('Description')
        doc.include_doc_string(operation.documentation)

    def doc_synopsis_start(self, help_command, **kwargs):
        doc = help_command.doc
        doc.style.h2('Synopsis')
        doc.style.start_codeblock()
        doc.writeln('%s' % help_command.name)

    def doc_synopsis_option(self, arg_name, help_command, **kwargs):
        doc = help_command.doc
        argument = help_command.arg_table[arg_name]
        option_str = argument.cli_name
        if argument.cli_type_name != 'boolean':
            option_str += ' <value>'
        if not argument.required:
            option_str = '[%s]' % option_str
        doc.writeln('%s' % option_str)

    def doc_synopsis_end(self, help_command, **kwargs):
        doc = help_command.doc
        doc.style.end_codeblock()

    def doc_options_start(self, help_command, **kwargs):
        doc = help_command.doc
        operation = help_command.obj
        doc.style.h2('Options')
        if len(operation.params) == 0:
            doc.write('*None*\n')

    def doc_option(self, arg_name, help_command, **kwargs):
        doc = help_command.doc
        argument = help_command.arg_table[arg_name]
        doc.write('``%s`` (%s)\n' % (argument.cli_name,
                                     argument.cli_type_name))
        doc.style.indent()
        doc.include_doc_string(argument.documentation)
        doc.style.dedent()
        doc.style.new_paragraph()

    def _json_example_value_name(self, param):
        if param.type == 'string':
            if hasattr(param, 'enum'):
                choices = param.enum
                return '|'.join(['"%s"' % c for c in choices])
            else:
                return '"string"'
        elif param.type == 'boolean':
            return 'true|false'
        else:
            return '%s' % param.type

    def _json_example(self, doc, param):
        if param.type == 'list':
            doc.write('[')
            if param.members.type in SCALARS:
                doc.write('%s, ...' % self._json_example_value_name(param.members))
            else:
                doc.style.indent()
                doc.style.new_line()
                self._json_example(doc, param.members)
                doc.style.new_line()
                doc.write('...')
                doc.style.dedent()
                doc.style.new_line()
            doc.write(']')
        elif param.type == 'map':
            doc.write('{')
            doc.style.indent()
            key_string = self._json_example_value_name(param.keys)
            doc.write('%s: ' % key_string)
            if param.members.type in SCALARS:
                doc.write(self._json_example_value_name(param.members))
            else:
                doc.style.indent()
                self._json_example(doc, param.members)
                doc.style.dedent()
            doc.style.new_line()
            doc.write('...')
            doc.style.dedent()
            doc.writeln('}')
        elif param.type == 'structure':
            doc.write('{')
            doc.style.indent()
            doc.style.new_line()
            for i, member in enumerate(param.members):
                if member.type in SCALARS:
                    doc.write('"%s": %s' % (member.py_name,
                        self._json_example_value_name(member)))
                elif member.type == 'structure':
                    doc.write('"%s": ' % member.py_name)
                    self._json_example(doc, member)
                elif member.type == 'map':
                    doc.write('"%s": ' % member.py_name)
                    self._json_example(doc, member)
                elif member.type == 'list':
                    doc.write('"%s": ' % member.py_name)
                    self._json_example(doc, member)
                if i < len(param.members) - 1:
                    doc.write(',')
                    doc.style.new_line()
                else:
                    doc.style.dedent()
                    doc.style.new_line()
            doc.write('}')

    def doc_option_example(self, arg_name, help_command, **kwargs):
        doc = help_command.doc
        argument = help_command.arg_table[arg_name]
        param = argument.argument_object
        if param.example_fn:
            doc.style.new_paragraph()
            doc.write('Shorthand Syntax')
            doc.style.start_codeblock()
            for example_line in param.example_fn(param).splitlines():
                doc.writeln(example_line)
            doc.style.end_codeblock()
        if param.type not in SCALARS:
            doc.style.new_paragraph()
            doc.write('JSON Syntax')
            doc.style.start_codeblock()
            self._json_example(doc, param)
            doc.style.end_codeblock()
            doc.style.new_paragraph()

    def doc_options_end(self, help_command, **kwargs):
        doc = help_command.doc
        operation = help_command.obj
        if hasattr(operation, 'filters'):
            doc.style.h2('Filters')
            sorted_names = sorted(operation.filters)
            for filter_name in sorted_names:
                filter_data = operation.filters[filter_name]
                doc.style.h3(filter_name)
                if 'documentation' in filter_data:
                    doc.include_doc_string(filter_data['documentation'])
                if 'choices' in filter_data:
                    doc.style.new_paragraph()
                    doc.write('Valid Values: ')
                    choices = '|'.join(filter_data['choices'])
                    doc.write(choices)
                doc.style.new_paragraph()
