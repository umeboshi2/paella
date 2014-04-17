# require config comes first
require.config
  baseUrl: ''
  paths:
    jquery: 'components/jquery/dist/jquery'
    underscore: 'components/lodash/dist/lodash.compat'
    backbone: '../../../components/backbone/backbone'
    'backbone.wreqr': 'components/backbone.wreqr/lib/backbone.wreqr'
    'backbone.babysitter': 'components/backbone.babysitter/lib/backbone.babysitter'
    marionette: 'components/marionette/lib/core/amd/backbone.marionette'
    validation: 'components/backbone.validation/dist/backbone-validation-amd'
    bootstrap: 'components/bootstrap/dist/js/bootstrap'
    'jquery-ui': 'components/jquery-ui/ui/jquery-ui'
    requirejs: 'components/requirejs/require'
    text: 'components/requirejs-text/text'
    teacup: 'components/teacup/lib/teacup'
    marked: 'components/marked/lib/marked'
    
    common: 'javascripts/coffee/common'

  # FIXME:  try to reduce the shim to only the
  # necessary resources
  shim:
    #jquery:
    #  exports: ['$', 'jQuery']
    bootstrap:
      deps: ['jquery']
    backbone:
    #  deps: ['underscore']
      exports: ['Backbone']
    'backbone.wreqr':
      deps: ['backbone']
      exports: ['Backbone.Wreqr']
    'backbone.babysitter':
      deps: ['backbone']
    marionette:
      deps: ['backbone']


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
        
        