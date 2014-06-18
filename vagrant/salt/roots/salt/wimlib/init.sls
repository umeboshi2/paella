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

# FIXME: find a better place for this state
salt-windows-installer-files-git-repos-cache:
  git.latest:
    - name: https://github.com/saltstack/salt-windows-install.git
    - target: ${reposdir}/salt-windows-install
    - user: ${pillar['paella_user']}
    - rev: 36a7b90f8a7b90aad25c5190fa032ab6eaf6a405


#salt-windows-installer-files:
#  git.latest:
#    - name: ${reposdir}/salt-windows-install
#    - target: /srv/shares/incoming/salt-windows-install
#    - user: ${pillar['paella_user']}


<% localrepo = '%s/wimlib-code' % reposdir %>

<% workspace = '/home/vagrant/workspace' %>

<% buildscript = '/home/vagrant/bin/build-wimlib-package' %>
build-wimlib-package-script:
  file.managed:
    - name: ${buildscript}
    - source: salt://scripts/build-wimlib-package.sh
    - mode: 755
    - user: ${pillar['paella_user']}
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

