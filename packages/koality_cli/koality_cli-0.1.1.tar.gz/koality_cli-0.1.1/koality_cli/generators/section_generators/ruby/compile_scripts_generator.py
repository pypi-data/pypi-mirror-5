import os.path

from koality_cli.generators.section_generators.section_generators import CompileScriptsSectionGenerator


class RubyCompileScriptsSectionGenerator(CompileScriptsSectionGenerator):
	def create_scripts_subsection(self):
		compile_scripts = []
		for index, directory in enumerate(self.dependency_files):
			if os.path.exists(os.path.join(self.repo_root, directory, "Gemfile")):
				compile_scripts.append(self._get_compile_section(
					'%s %d' % ("bundle install", index),
					directory,
					"bundle install"))
		return compile_scripts
