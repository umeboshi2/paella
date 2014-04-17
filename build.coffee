(
  baseUrl: 'javascripts/coffee/paella'
  mainConfigFile: 'javascripts/coffee/paella/main.js'
  paths:
    requireLib: '../../../components/requirejs-bower/require'
    jquery: '../../../components/jquery/dist/jquery'
    underscore: '../../../components/lodash/dist/lodash.compat'
    backbone: '../../../components/backbone/backbone'
    'backbone.wreqr': '../../../components/backbone.wreqr/lib/backbone.wreqr'
    'backbone.babysitter': '../../../components/backbone.babysitter/lib/backbone.babysitter'
    marionette: '../../../components/marionette/lib/core/amd/backbone.marionette'
    validation: '../../../components/backbone.validation/dist/backbone-validation-amd'
    bootstrap: '../../../components/bootstrap/dist/js/bootstrap'
    'jquery-ui': '../../../components/jquery-ui/ui/jquery-ui'
    requirejs: '../../../components/requirejs/require'
    text: '../../../components/requirejs-text/text'
    teacup: '../../../components/teacup/lib/teacup'
    marked: '../../../components/marked/lib/marked'
    
    common: '../common'
  name: 'main'
  out: 'javascripts/paella-built.js'
  include: ['requireLib']
  wrapShim: true
  optimize: 'uglify'
  uglify:
    no_mangle: false
    no_mangle_functions: false
)