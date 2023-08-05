Lilac
=====

Lilac is a MIT Licensed static blog generator, written in Python. It's fast, simple enough and easy to use.

Documentation is already on https://lilac.readthedocs.org/

**Lilac may not be stable since the v1.0 hasn't come.** 

Features
--------

- TOML and GFM based.
- 100% in Python (any linux distribution comes with python)
- Built-in tags & feed & theme & codes highlighting support
- We use Jinja2 to render templates.
- No categories, only tags. (It's A GOOD FEATURE!)
- Minimal configuration.

Demo Sites
----------

- [Make Difference](http://lilac.hit9.org/), repo: https://github.com/hit9/lilac/tree/gh-pages

- [Make Difference](http://lilac-less.hit9.org/), repo: https://github.com/hit9/lilac-theme-less/tree/gh-pages

- [Follow My Heart](http://hit9.org), repo: https://github.com/hit9/hit9.github.com

Install
-------

```bash
$ mkdir MyBlog
$ cd MyBlog
$ virtualenv venv
New python executable in venv/bin/python
Installing setuptools............done.
Installing pip...............done.
$ . venv/bin/activate
$ pip install -e "git+git://github.com/hit9/lilac.git#egg=lilac" --upgrade
```

Sample Post
-----------

A post is made up of two parts: header and body.

The header is in [TOML](https://github.com/mojombo/toml) and body is in Github Flavored Markdown,
the two parts are separated with a '---' like separator.

```
title = "Hello World"
datetime = "2013-06-05 19:38"
tags = ["sample", "some-tag"]
----------

# Here is markdown content
```

Commands
---------

Show help:

    $ lilac --help

Show version:

    $ lilac --version

To deploy a new blog in new-created directory:

    $ lilac deploy

To build site from source to htmls:

    $ lilac build

To remove all htmls lilac built:

    $ lilac clean

To start a simple HTTP server:

    $ lilac serve

You can tell lilac which port to use(the default port is 8888):

    $ lilac serve 8080

To watch source changes the same time when the cute web server running:

    $ lilac serve --watch

When you save your writings, lilac can detect the changes and start rebuilding.

Themes
------

You really should manage your theme in a standalone git repository, and use it as a submodule of your blog's
submodule if your blog is under git versioning too.

For instance, add theme classic a submodule of your blog's repo:

    $ git submodule add git://github.com/hit9/lilac-theme-classic.git classic

If you want to modify a theme created by someone else(i.e. classic), just fork his(or her) repo, and then modify it.

But it's 100% ok to use themes not in the submodule way.

Theme list:

- [classic](https://github.com/hit9/lilac-theme-classic) - the default theme for lilac. by @hit9
- [less](https://github.com/hit9/lilac-theme-less) - a clean theme for lilac. by @hit9

Have you made one? Please send a pull request on lila's repo, append yours to this list.

Documents
---------

- English version: https://lilac.readthedocs.org/

- 简体中文版本: https://lilac-zh.readthedocs.org

Help Us
-------

Found a bug? Have a good idea for improving Lilac?
You can fork lilac's repo and then send a feature pull request, or you can open a new
[issue](https://github.com/hit9/lilac/issues) to report bugs, that will help all users. Welcome for your feedback.
