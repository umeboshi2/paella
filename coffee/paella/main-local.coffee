# require config comes first
require.config
  baseUrl: 'javascripts/coffee/paella'
  paths:
    jquery: '../../../components/jquery/dist/jquery'
    underscore: '../../../components/lodash/dist/lodash.compat'
    backbone: '../../../components/backbone/backbone'
    marionette: '../../../components/marionette.bundle/index'
    validation: '../../../components/backbone.validation/dist/backbone-validation-amd'
    bootstrap: '../../../components/bootstrap/dist/js/bootstrap'
    'jquery-ui': '../../../components/jquery-ui/ui/jquery-ui'
    requirejs: '../../../components/requirejs/require'
    text: '../../../components/requirejs-text/text'
    teacup: '../../../components/teacup/lib/teacup'
    marked: '../../../components/marked/lib/marked'
    
    common: '../common'

  # FIXME:  try to reduce the shim to only the
  # necessary resources
  shim:
    jquery:
      exports: ['$', 'jQuery']
    bootstrap:
      deps: ['jquery']
    underscore:
      exports: '_'
    backbone:
      deps: ['jquery', 'underscore']
      exports: 'Backbone'
    marionette:
      deps: ['jquery', 'underscore', 'backbone']
      exports: 'Marionette'


requirements = [
  'application'
  'frontdoor/main'
  ]

require [
  'application'
  'frontdoor/main'
  ], (App) ->
  # debug
  window.app = App
  
  start_app_one = () ->
    if App.ready == false
      setTimeout(start_app_two, 100)
    else
      App.start()
        
  start_app_two = () ->
    if App.ready == false
      setTimeout(start_app_one, 100)
    else
      App.start()
    
  start_app_one()
  return App
        
        