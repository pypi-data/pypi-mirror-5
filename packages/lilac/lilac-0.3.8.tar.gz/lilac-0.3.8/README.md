Lilac
=====

Lilac is a MIT Licensed static blog generator, written in Python. It's fast, simple enough and easy to use.

Latest version: v0.3.8

Documentation is already on readthedocs: [English Version](https://lilac.readthedocs.org/), [简体中文版本](https://lilac-zh.readthedocs.org)

News about lilac is here: http://lilac.hit9.org/

![](./screen-shots/post.png)

Features
--------

- TOML and GFM based.
- 100% in Python (any linux distribution comes with python)
- Built-in Tags & Feed & Theme & Code Highlighting support
- We use Jinja2 to render templates.
- No categories, only tags. (It's A GOOD FEATURE!)
- Minimal configuration.

Demo Sites
----------

- [Lilac News](http://lilac.hit9.org/), repo: https://github.com/hit9/lilac-website/tree/gh-pages

- [Make Difference](http://lilac-less.hit9.org/), repo: https://github.com/hit9/lilac-theme-less/tree/gh-pages

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
$ pip install lilac
```

Installation troubles:

- cann't find Python.h. Solution: install `python-dev` package (on ubuntu: `sudo apt-get install python-dev`. There's no such issue on OSX)

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

To deploy a new blog in new-created directory:

    $ lilac deploy

To build site from source to htmls:

    $ lilac build

To remove all htmls lilac built:

    $ lilac clean

To start a simple HTTP server:

    $ lilac serve

To watch source changes the same time when the cute web server running:

    $ lilac serve --watch

When you save your writings, lilac can detect the changes and start rebuilding.

Themes
------

You really should manage your theme in a standalone git repository, and use it as a submodule of your blog's
submodule if your blog is under git versioning too.

For instance, add theme `less` a submodule of your blog's repo:

    $ git submodule add git://github.com/hit9/lilac-theme-less.git less

If you want to modify a theme created by someone else, just fork his(or her) repo, and then modify it.

But it's 100% ok to use themes not in the submodule way.

Theme list:

- [classic](https://github.com/hit9/lilac-theme-classic) -  by @hit9
- [less](https://github.com/hit9/lilac-theme-less) - a clean theme for lilac. by @hit9 (now it's the default theme)
- [pure](https://github.com/kshiftlv/lilac-theme-pure) - a clean theme for lilac by @kshiftlv

Have you made one? Please send a pull request on lila's repo, append yours to this list.

Tools
-------

- ililac - a tool to run lilac's server and rebuilder in the background(included in v0.3.7):

  ```bash
  $ cd myblog
  $ ililac start
  ```

  to stop the daemon:

  ```bash
  $ ililac stop
  ```

  With this tool, we can write blog with at most one shell session.

Documents
---------

- English version: https://lilac.readthedocs.org/

- 简体中文版本: https://lilac-zh.readthedocs.org

Help Us
-------

Found a bug? Have a good idea for improving Lilac?
You can fork lilac's repo and then send a feature pull request, or you can open a new
[issue](https://github.com/hit9/lilac/issues) to report bugs, that will help all users. Welcome for your feedback.
