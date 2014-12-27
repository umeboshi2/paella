# set path to components
components = '../../components'
# require config comes first
require.config
  baseUrl: '/paella/client/javascripts/chassis'
  paths:
    jquery: "#{components}/jquery/dist/jquery"
    underscore: "#{components}/lodash/dist/lodash.compat"
    backbone: "#{components}/backbone/backbone"
    'backbone.babysitter': "#{components}/backbone.babysitter/lib/backbone.babysitter"
    'backbone.wreqr': "#{components}/backbone.wreqr/lib/backbone.wreqr"
    marionette: "#{components}/marionette/lib/core/backbone.marionette"
    validation: "#{components}/backbone.validation/dist/backbone-validation-amd"
    bblocalStorage: "#{components}/backbone.localStorage/backbone.localStorage"
    'backbone.paginator': "#{components}/backbone.paginator/lib/backbone.paginator"
    bootstrap: "#{components}/bootstrap/dist/js/bootstrap"
    moment: "#{components}/moment/moment"
    fullcalendar: "#{components}/fullcalendar/dist/fullcalendar"
    'jquery-ui': "#{components}/jquery-ui/jquery-ui"
    requirejs: "#{components}/requirejs/require"
    text: "#{components}/requirejs-text/text"
    teacup: "#{components}/teacup/lib/teacup"
    marked: "#{components}/marked/lib/marked"
    ace: "#{components}/ace/lib/ace"
    'matches-selector': "#{components}/matches-selector"
    'jquery.bridget': "#{components}/jquery-bridget/jquery.bridget"
    'doc-ready': "#{components}/doc-ready"
    eventEmitter: "#{components}/eventEmitter"
    'get-size': "#{components}/get-size"
    eventie: "#{components}/eventie"
    'get-style-property': "#{components}/get-style-property"
    masonry: "#{components}/masonry/masonry"
    outlayer: "#{components}/outlayer"
    imagesloaded: "#{components}/imagesloaded/imagesloaded"
    
    # common is the path to the common modules
    # These should maybe be packaged as bower
    # component.
    common: '../common'
    # applets
    hubby: '../applets/hubby'
    bumblr: '../applets/bumblr'
    wiki: '../applets/wiki'
    frontdoor: '../applets/frontdoor'
    bookstore: '../applets/bookstore'
    diskrecipes: '../applets/diskrecipes'
    machines: '../applets/machines'
    
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
    bblocalStorage:
      deps: ['backbone']
      exports: 'Backbone.localStorage'

require [
  'application'
  'common/util'
  'frontdoor/main'
  ], (App, Util) ->
  # debug
  window.app = App
  # simple app starter
  return Util.start_application(App)
        
        
