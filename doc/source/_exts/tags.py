#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""Show information about tagged projects.
"""

from docutils import nodes
from docutils.parsers import rst
from docutils.statemachine import ViewList
from sphinx.util.nodes import nested_parse_with_titles

import projects

_projects_by_tag = {}


class TaggedProjectsDirective(rst.Directive):
    """List the projects tagged with the given tag.
    """

    has_content = True

    def run(self):
        env = self.state.document.settings.env
        app = env.app

        tagname = ' '.join(self.content)
        app.info('building list of projects tagged %r' % tagname)
        if not tagname:
            error = self.state_machine.reporter.error(
                'No tagname in tagged-projects directive',
                nodes.literal_block(self.block_text, self.block_text),
                line=self.lineno)
            return [error]

        # Build the view of the data to be parsed for rendering.
        result = ViewList()
        project_data = _projects_by_tag.get(tagname)
        source_name = '<' + __name__ + '>'
        if not project_data:
            result.append(
                '.. note:: No projects are using %s, yet.' % tagname,
                source_name,
            )
        else:
            for team_name, repo in sorted(project_data):
                if repo is None:
                    line = '- :ref:`project-%s`' % projects.slugify(team_name)
                else:
                    line = '- :ref:`project-%s` -- :repo:`%s`' % (
                        projects.slugify(team_name),
                        repo,
                    )
                result.append(line, source_name)

        # Parse what we have into a new section.
        node = nodes.section()
        node.document = self.state.document
        nested_parse_with_titles(self.state, result, node)

        return node.children


def _build_projects_by_tag():
    for proj_name, info in projects.get_project_data().items():
        for tag in info.get('tags', []):
            tn = tag['name']
            l = _projects_by_tag.setdefault(tn, [])
            l.append((proj_name, None))
        for repo in info.get('projects', []):
            for tag in repo.get('tags', []):
                tn = tag['name']
                l = _projects_by_tag.setdefault(tn, [])
                l.append((proj_name, repo['repo']))


def setup(app):
    app.info('loading tags extension')
    _build_projects_by_tag()
    app.add_directive('tagged-projects', TaggedProjectsDirective)
