(
  baseUrl: 'javascripts/paella'
  mainConfigFile: 'javascripts/paella/main.js'
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
    'backbone.paginator': '../../components/backbone.paginator/lib/backbone.paginator'
    marionette: '../../components/marionette/lib/core/backbone.marionette'
    validation: '../../components/backbone.validation/dist/backbone-validation-amd'
    bootstrap: '../../components/bootstrap/dist/js/bootstrap'
    moment: '../../components/moment/moment'
    fullcalendar: '../../components/fullcalendar/dist/fullcalendar'
    'jquery-ui': '../../components/jquery-ui/jquery-ui'
    requirejs: '../../components/requirejs/require'
    text: '../../components/requirejs-text/text'
    teacup: '../../components/teacup/lib/teacup'
    marked: '../../components/marked/lib/marked'
    ace: '../../components/ace/lib/ace'
    'matches-selector': "../../components/matches-selector"
    'jquery.bridget': "../../components/jquery-bridget/jquery.bridget"
    'doc-ready': "../../components/doc-ready"
    eventEmitter: "../../components/eventEmitter"
    'get-size': "../../components/get-size"
    eventie: "../../components/eventie"
    'get-style-property': "../../components/get-style-property"
    masonry: "../../components/masonry/masonry"
    outlayer: "../../components/outlayer"
    imagesloaded: "../../components/imagesloaded/imagesloaded"
    
    common: '../common'
    # applets
    hubby: '../applets/hubby'
    bumblr: '../applets/bumblr'
    wiki: '../applets/wiki'
    frontdoor: '../applets/frontdoor'
    bookstore: '../applets/bookstore'
    
  name: 'main'
  out: 'javascripts/paella-built.js'
  include: ['requireLib']
  wrapShim: true
  optimize: 'uglify'
  uglify:
    no_mangle: false
    no_mangle_functions: false
)
