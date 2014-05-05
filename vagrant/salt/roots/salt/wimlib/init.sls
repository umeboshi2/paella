# -*- mode: yaml -*-

#####################################

# paella-client
# 
# the local debian repository must be ready

include:
  - debrepos
  - default
  - schroot


<% cachedir = '/vagrant/vagrant/cache' %>

cache-repos-dir:
  file.directory:
    - name: ${cachedir}/repos
    - makedirs: True

<% reposdir = '%s/repos' % cachedir %>

cache-wimlib-git-repos:
  git.latest:
    - name: git://git.code.sf.net/p/wimlib/code
    - target: ${reposdir}/wimlib-code
    - user: ${pillar['paella_user']}
    - rev: 8682c564e55aae964457f183a9b860de3631d4d1

<% localrepo = '%s/wimlib-code' % reposdir %>

<% workspace = '/home/vagrant/workspace' %>

<% buildscript = '/home/vagrant/bin/build-wimlib-package' %>
build-wimlib-package-script:
  file.managed:
    - name: ${buildscript}
    - source: salt://scripts/build-wimlib-package.sh
    - mode: 755
    - makedirs: True


%for arch in ['i386', 'amd64']:

# FIXME this is stupid
<% archspace = '%s/%s' % (workspace, arch) %>

wimlib-workspace-dir-${arch}:
  file.directory:
    - name: ${archspace}
    - makedirs: True
    - user: ${pillar['paella_user']}


wimlib-git-repos-${arch}:
  git.latest:
    - name: ${localrepo}
    - target: ${archspace}/wimlib-code
    - user: ${pillar['paella_user']}
    - rev: 8682c564e55aae964457f183a9b860de3631d4d1
    - require:
      - file: wimlib-workspace-dir-${arch}

<% builddir = '%s/wimlib-code' % archspace %>

# This darned command should almost be a script.
# In order to keep the development base and partial
# debian repository reasonably small, the building 
# of the doc package is bypassed.  The tests are 
# also bypassed as they require extra build depends,
# as well as being root, instead of fakeroot.  The
# tests for this build passed when the package was 
# built manually.
build-wimlib-package-${arch}:
  cmd.run:
    - require:
      - cmd: upload-paella-client-package
      - file: build-wimlib-package-script
    - unless: test -r ${archspace}/wimlib_1.6.2-1_${arch}.changes
    %if arch == 'amd64':
    - name: ${buildscript}
    %elif arch == 'i386':
    - name: schroot -c wheezy32 ${buildscript}
    %else:
    - name: /bin/false
    %endif
    - cwd: ${builddir}
    - user: ${pillar['paella_user']}


upload-wimlib-package-${arch}:
  cmd.run:
    - require:
      - cmd: build-wimlib-package-${arch}
    - unless: test -n "`reprepro -b /srv/debrepos/paella list wheezy wimtools | grep ${arch}`"
    - cwd: ${archspace}
    - name: reprepro -b /srv/debrepos/paella --ignore=wrongdistribution include wheezy wimlib_1.6.2-1_${arch}.changes
    - user: ${pillar['paella_user']}
%endfor

