# require config comes first
require.config
  baseUrl: 'common/app'
  paths:
    jquery: '/components/jquery/jquery'
    ace: '/components/ace/lib/ace'
    backbone: '/components/backbone/backbone'
    bootstrap: '/components/bootstrap/dist/js/bootstrap'
    'jquery-ui': '/components/jquery-ui/ui/jquery-ui'
    requirejs: '/components/requirejs/require'
    underscore: '/components/underscore/underscore'
  shim:
    backbone:
      deps: ['underscore', 'jquery']
      exports: 'Backbone'
    underscore:
      exports: '_'
    jquery:
      exports: ['$', 'jQuery']
    teacup:
      exports: ['teacup']
    bootstrap:
      deps: ['jquery']


require ['application', 'router', 'backbone'],
(Application, Router, Backbone) ->
  app = new Application()
  router = new Router app
  window.app = app
  Backbone.history.start()
