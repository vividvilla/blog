# -*- coding: utf-8 -*-
"""
	Olaf
	~~~~~~~~~

	Olaf command line utility

	:copyright: (c) 2015 by Vivek R.
	:license: BSD, see LICENSE for more details.
"""

import os
import sys
import shutil

import click

from olaf import app
from olaf.utils import slugify
from olaf import module_path, current_dir, \
	is_valid_path, is_valid_site, get_themes_list, get_theme_by_name, \
	get_default_theme_name, create_project_site


@click.group()
def cli():
	"""
	Olaf command line utility
	"""
	pass


@cli.command()
@click.argument('project_name', type=str, required=True)
@click.option('-d', '--demo', type=bool, default=True)
def createsite(project_name, demo):
	"""
	create a blog
	"""
	project_name = slugify(project_name)  # santize project name
	create_project_site(project_name)
	click.secho('site "{}" has been successfully created'.format(
		project_name), fg='green')

	# populate demo files (True by default)
	if demo:
		shutil.copyfile(
			os.path.join(module_path, 'demo-files', 'hello-world.md'),
			os.path.join(
				current_dir, project_name, '_contents',
				'posts', 'hello-world.md'))

		shutil.copyfile(
			os.path.join(module_path, 'demo-files', 'typography.md'),
			os.path.join(
				current_dir, project_name, '_contents',
				'posts', 'typography.md'))

		shutil.copyfile(
			os.path.join(module_path, 'demo-files', 'sample-page.md'),
			os.path.join(
				current_dir, project_name, '_contents',
				'pages', 'sample-page.md'))

	click.secho('demo files successfully populated', fg='green')


@cli.command()
@click.option(
	'-t', '--theme', help='blog theme (default: basic)')
@click.option(
	'-p', '--port', default=5000, help='port to run (default: 5000)')
@click.option(
	'-h', '--host', default='localhost',
	help='hostname to run (default: localhost)')
def run(theme, port, host):
	"""
	run olaf local server
	"""

	# check for a valid site directory
	is_valid_site()

	# get specified theme path
	theme_name = get_default_theme_name(theme)
	theme_path = get_theme_by_name(theme_name)
	if not theme_path:
		# sepcified theme not found
		click.secho(
			'Sepcified theme "{}" not found'.format(theme_name), fg='red')
		sys.exit(0)

	try:
		app_ = app.create_app(current_dir, theme_path)
		app_.run(port=port, host=host)
	except ValueError as e:
		click.secho(e, fg='red')


@cli.command()
@click.option(
	'-t', '--theme', default='basic', help='blog theme (default: basic)')
@click.option(
	'-p', '--path', default='',
	help='Freeze directory (default: current directory)')
@click.option(
	'-s', '--static', default=False, type=bool, help='Freeze with relative urls'
	'(Run without web server) (default: False)')
def freeze(theme, path, static):
	"""
	freeze blog to static files
	"""
	# check for a valid site directory
	is_valid_site()

	# get specified theme path
	theme_name = get_default_theme_name(theme)
	theme_path = get_theme_by_name(theme_name)
	if not theme_path:
		# sepcified theme not found
		click.secho(
			'Sepcified theme "{}" not found'.format(theme_name), fg='red')
		sys.exit(0)

	if path:
		path = os.path.join(current_dir, slugify(path))
	else:
		path = current_dir

	try:
		# create app
		app_ = app.create_app(
			current_dir,
			theme_path,
			freeze_path=path,
			freeze_static=static)
		app.freeze.freeze()

		if not os.path.exists(os.path.join(path, '.nojekyll')):
			open(os.path.join(path, '.nojekyll'), 'a').close()

		click.secho('successfully freezed app', fg='green')
	except ValueError as e:
		click.secho(e, fg='red')


@cli.command()
@click.option(
	'-p', '--path', default='',
	help='Directory where site has been freezed (default: current directory)')
@click.option(
	'-m', '--message', default='new update', help='commit message')
@click.option(
	'-b', '--branch', default='master',
	help='branch to be pushed (default: master)')
def git(path, message, branch):
	"""
	Git uploader tool
	"""
	full_path = os.path.join(current_dir, path)
	is_valid_path(os.path.join(current_dir, path))

	from olaf.tools import git
	git.upload(full_path, message, branch)


@cli.command()
@click.option(
	'-p', '--path', default='',
	help='Directory where site has been freezed (default: current directory)')
def cname(path):
	"""
	Update CNAME file
	"""
	full_path = os.path.join(current_dir, path)
	is_valid_path(os.path.join(current_dir, path))

	from olaf.tools import git
	git.update_cname(full_path)


@cli.command()
@click.option(
	'-p', '--pygments-styles', count=True, help='Get list of pygments styles')
@click.option(
	'-i', '--inbuilt-themes', count=True, help='Get list of inbuilt themes')
@click.option(
	'-t', '--themes', count=True, help='Get list of all themes')
def utils(pygments_styles, inbuilt_themes, themes):
	"""
	olaf utils
	"""

	if pygments_styles:
		from pygments.styles import STYLE_MAP
		styles = STYLE_MAP.keys()
		click.secho('list of pygments styles', fg='cyan')
		for style in styles:
			if style == 'tango':
				click.echo('tango' + click.style(' (default)', fg='green'))
			else:
				click.echo(style)

	if inbuilt_themes or themes:
		inbuilt_themes_list = get_themes_list(os.path.join(module_path, 'themes'))

		click.secho('list of inbuilt themes', fg='blue', bold=True)
		for theme in inbuilt_themes_list:
			if theme['name'] == 'basic':
				click.secho(
					' - ' + theme['name'] + click.style(' (default)', fg='green'))
			else:
				click.echo(theme['name'])

			if not inbuilt_themes_list:
				click.secho(' - no inbuilt themes available', fg='red')

		if themes:
			custom_themes_list = get_themes_list(
				os.path.join(current_dir, 'themes'))
			click.secho('list of custom themes', fg='blue', bold=True)
			for theme in custom_themes_list:
				click.echo(' - ' + theme['name'])

			if not custom_themes_list:
				click.secho(' - no custom themes available', fg='red')


@cli.command()
def importer():
	"""
	Importer tools
	"""
	pass


@cli.command()
def export():
	"""
	Export tools
	"""
	pass