#!/usr/bin/env python

import sys
import os
import logging
import hashlib
from distutils.dir_util import copy_tree
import re
import pkg_resources
from optparse import OptionParser
from minitage.core.cli import get_minimerge

DATA = pkg_resources.resource_filename(
    pkg_resources.Requirement.parse('minitage'),
    'minitage/core/cfgs')

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT, level=logging.DEBUG)
logger =logging.getLogger('mintagify')
logger.setLevel(0)

parser = OptionParser()
parser.add_option("-d", "--directory", dest="directory",
                  help="project to minitagify eg ~/minitage/zope/myproject",)

re_flags = re.S|re.U|re.X
targets = [
    #(re.compile('.*zeo.*\.cfg', re_flags),'minitagezeo.cfg',),
    (re.compile('.*4\.?2.*\.cfg'  , re_flags),'minitage27.cfg', ),
    (re.compile('.*4\.?0.*\.cfg'  , re_flags),'minitage26.cfg', ),
    (re.compile('.*4\.?1.*\.cfg'  , re_flags),'minitage26.cfg', ),
    (re.compile('.*\.cfg'      , re_flags),'minitage27.cfg', ),
]
pythons = [
    (re.compile('.*zeo.*\.cfg',     re_flags), 'python-2.7',),
    (re.compile('.*4\.?2.*\.cfg'  , re_flags), 'python-2.7', ),
    (re.compile('.*4\.?0.*\.cfg'  , re_flags), 'python-2.6', ),
    (re.compile('.*4\.?1.*\.cfg'  , re_flags), 'python-2.6', ),
    (re.compile('.*\.cfg'      ,    re_flags), 'python-2.7', ),
]

TEMPLATE = """
[buildout]
extends-cache=.cache
extends=%(orig)s %(wrapper)s
"""

def isbuildout(cfg):
    ret = False
    if os.path.isfile(cfg):
        data = open(cfg).read()
        if (
             not re.search('\/minitage.[^/]*\.cfg', cfg)
            and not re.search('\/\.[^/]*\.cfg', cfg)
            and ('[buildout]' in data or '[versions]' in data)
        ):
            ret = True
    return ret



def relative(path1, path2):
    if path2.startswith(path1):
        path1, path2 = path2, path1
    pt = os.path.relpath(path1, path2)
    return pt


def sbuildouts(directory):
    contents = os.listdir(directory)
    bs =  [os.path.join(directory, a)
            for a in contents
            if isbuildout(os.path.join(directory, a))]
    plips = os.path.join(directory, 'plips')
    if 'plips' in contents:
        bs += [os.path.join(plips, a)
               for a in os.listdir(plips)
               if isbuildout(os.path.join(plips, a))]
    bs = [a for a in bs if not a.startswith('minitage')]
    return bs

def make_minilay(directory, buildouts):
    minimerge = get_minimerge(read_options=False)
    default_minibuild = os.path.basename(directory)
    categ = os.path.basename(os.path.dirname(directory))
    minilayname = '0-%s_%s' % (
        default_minibuild,
        hashlib.md5(directory).hexdigest()
    )
    minilaytarget = os.path.join(minimerge.minilays_parent, minilayname)
    minilaydir = os.path.join(
        directory, '.minitagecfg', minilayname)
    minibuild = os.path.join(minilaydir, os.path.basename(directory))
    if not len(buildouts):
        buildouts.append(
            os.path.join(directory, 'buildout.cfg'))
    if not os.path.isdir(minilaydir):
        os.makedirs(minilaydir)
    MINIBUILDS = []
    MCONTENT = open(os.path.join(DATA, 'minibuild')).read()
    MCONTENT = re.sub('category=.*',
                      'category=%s'% categ, MCONTENT)
    configs_mapping = dict([(os.path.basename(a),
                             buildouts[a])
                            for a in buildouts])

    def minibuild(cfg):
        minibuild_content = MCONTENT
        minibuild_content = re.sub(
            'buildout_config=.*',
            'buildout_config=%s' % (
                os.path.basename(
                    configs_mapping.get(
                        cfg, 'minitage.buildout.cfg'
                    )
                )
            )
            ,minibuild_content
        )
        python = 'python-2.7'
        for match, c in pythons:
            if match.search(cfg):
                python = c
                break
        minibuild_content = minibuild_content.replace('python-xxx', python)
        return minibuild_content

    for i in buildouts:
        cfg = os.path.basename(i)
        mname = '%s-%s' % (
            default_minibuild,
            cfg.replace('.cfg', ''))
        mpath = os.path.join(minilaydir, mname)
        mnb = minibuild(cfg)
        MINIBUILDS.append((mpath, mname, mnb))
    if not default_minibuild in [a[1] for a in MINIBUILDS]:
        MINIBUILDS.append(
            (os.path.join(minilaydir, default_minibuild),
             default_minibuild,
             minibuild('buildout.cfg')))
    for mpath, mname, minibuild_content in MINIBUILDS:
        logger.warn('Wroted minibuild %s in %s' % (mname, mpath))
        f = open(mpath, 'w')
        f.write(minibuild_content)
        f.close()
    if os.path.exists(minilaytarget):
        os.unlink(minilaytarget)
    os.symlink(
        relative(minilaydir, minimerge.minilays_parent), 
        minilaytarget)
    logger.warn(
        "Installed minilay %s by symlink: %s" %(
            os.path.abspath(
                relative(minilaydir, minimerge.minilays_parent)
            ), 
            minilaytarget))
        

def wrap(buildout, directory=None):
    if not directory:
        directory = os.path.dirname(buildout)
    buildout_dir = os.path.dirname(buildout)
    buildout_name = os.path.basename(buildout)
    prefix = relative(
        directory,
        os.path.dirname(buildout)
    ).replace('/', '_').replace('.', '_')
    if prefix and prefix != '_': prefix += '-'
    else: prefix = ''
    m = os.path.join(directory, '.minitagecfg')
    cache = os.path.join(directory, '.cache')
    newcfg = prefix+buildout_name
    b = os.path.join(m, newcfg)
    d = os.path.join(directory, 'minitage.%s' % newcfg)
    cfg = ''
    for match, config in targets:
        if match.search(buildout):
            cfg = config
            break
    if not cfg:
        logger.warn('%s cant be wrapped!' % buildout)
    logger.warn(
        "Wraping %s (%s) in %s->%s" % (buildout, config, d, b))
    if not os.path.isdir(cache): os.makedirs(cache)
    if not os.path.isdir(m): os.makedirs(m)
    copy_tree(os.path.join(DATA, 'wrap'), m)
    f = open(b, 'w')
    cfgwrap = relative(directory, os.path.join(m, cfg))
    if not cfg in cfgwrap:
        cfgwrap = relative(os.path.join(m, cfg), directory)
    contents = TEMPLATE % {
        'orig': relative(directory, buildout),
        'wrapper': cfgwrap
    }
    if "plip" in buildout:
        contents += PLIP
    f.write(contents)
    if os.path.exists(d): os.unlink(d)
    os.symlink(b, d)
    f.close()
    return d

PLIP = """
[buildout]
develop-eggs-directory = develop-eggs
bin-directory = ${buildout:directory}/bin
parts-directory = ${buildout:directory}/parts
sources-dir = ${buildout:directory}/src
installed = ${buildout:directory}/.installed.cfg
[instance]
var = ${buildout:directory}/var
"""


def main():
    (options, args) = parser.parse_args()
    if not options.directory:
        print parser.print_help()
        raise Exception ('-d missing')
    directory = os.path.abspath(
        os.path.expanduser(options.directory)
    )
    if not os.path.exists(options.directory):
        raise Exception ('%s does not exist' % options.directory)
    if not os.path.isdir(options.directory):
        raise Exception ('%s is not a dir' % options.directory)
    buildouts = sbuildouts(directory)
    # TODO: give a template to choose other than plone addon
    INFRA = os.path.join(DATA, 'addon')
    if not buildouts:
        copy_tree(INFRA, directory)
    buildouts = sbuildouts(directory)
    installed = {}
    for i in buildouts:
        try:
           installed[i] = wrap(i, directory)
        except Exception, e:
            logger.warn('cant wrap; %s' % i)
    helper = os.path.join(directory, '.minitagecfg', 'b.sh')
    dhelper = os.path.join(
        directory, os.path.basename(helper))
    if not os.path.exists(dhelper):
        os.symlink( helper, dhelper)
    make_minilay(directory, installed)
    sys.stdout.flush()

if __name__ == '__main__':
    main()

# vim:set et sts=4 ts=4 tw=80:
