(
  baseUrl: 'javascripts/conspectus'
  mainConfigFile: 'javascripts/conspectus/main.js'
  paths:
    # these paths are relative the the main
    # config file above.  The base url is
    # relative to the directory this file is in
    # and the everything 'required' that is not
    # a component below is relative to that path.
    requireLib: '../../components/requirejs/require'
    jquery: '../../components/jquery/dist/jquery'
    underscore: '../../components/lodash/dist/lodash.compat'
    backbone: '../../components/backbone/backbone'
    'backbone.babysitter': '../../components/backbone.babysitter/lib/backbone.babysitter'
    'backbone.wreqr': '../../components/backbone.wreqr/lib/backbone.wreqr'
    marionette: '../../components/marionette/lib/core/backbone.marionette'
    validation: '../../components/backbone.validation/dist/backbone-validation-amd'
    'backbone.paginator': '../../components/backbone.paginator/lib/backbone.paginator'
    bootstrap: '../../components/bootstrap/dist/js/bootstrap'
    teacup:    '../../components/teacup/lib/teacup'
    marked: '../../components/marked/lib/marked'
    ace: '../../components/ace/lib/ace'
    
    common: '../common'
    # applets
    frontdoor: '../applets/frontdoor'
    
  name: 'main'
  out: 'javascripts/paella-built.js'
  include: ['requireLib']
  wrapShim: true
  optimize: 'uglify'
  uglify:
    no_mangle: false
    no_mangle_functions: false
)
