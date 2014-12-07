import os, sys

jquery_ui_template = """\
@import "partials/themes/%(basecolor)s";
@import "partials/absolution";
@include jquery-ui-base-theme;
"""

bootstrap_template = """\
@import "partials/themes/%(basecolor)s";
@import "partials/bootstrap-variables";
@import "bootstrap";
@import "partials/bootstrap-main";
"""

screen_template = """\
@import "partials/themes/%(basecolor)s";
@import "partials/listviews";
@import "partials/hubby";
@import "partials/screen-main";
"""

TEMPLATES = dict(jqueryui=jquery_ui_template,
                 screen=screen_template)
TEMPLATES['bootstrap-custom'] = bootstrap_template


BASECOLORS = ['bisque', 'BlanchedAlmond',
              'DarkSeaGreen', 'LavenderBlush',
              'PaellaDefault',
              ]

def generate_scss(basecolor, name, template):
    filename = '%s-%s.scss' % (name, basecolor)
    path = os.path.join('sass', filename)
    env = dict(basecolor=basecolor)
    with file(path, 'w') as o:
        o.write(template % env)
        
        

def generate_all_scss(basecolors):
    for basecolor in basecolors:
        for name, template in TEMPLATES.items():
            generate_scss(basecolor, name, template)

    # prepare font-awesome
    with file('sass/font-awesome.scss', 'w') as o:
        o.write('@import "partials/fontawesome/font-awesome";\n')
        
            
if __name__ == '__main__':
    generate_all_scss(BASECOLORS)
    
    
    
