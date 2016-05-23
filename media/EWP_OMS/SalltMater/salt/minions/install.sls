epel_repo:
  file.managed:
    - name: /etc/yum.repos.d/epel.repo
    - source: salt://minions/files/epel.repo

salt_pkg:
  pkg.installed:
    - name: salt-minion
    - skip_verify: True
    - skip_suggestions: True
    - require:
      - file: epel_repo

salt_conf:
  file.managed:
    - name: /etc/salt/minion
    - source: salt://minions/files/minion
    - template: jinja
    - mode: 640
    - user: root
    - defaults:
      minion_id: {{grains['fqdn']}}
    - require:
      - pkg: salt_pkg

salt_service:
  service.running:
    - name: salt-minion
    - enable: True
    - restart: True
    - watch:
      - file: salt_conf
    - require:
      - pkg: salt_pkg
