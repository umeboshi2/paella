define (require, exports, module) ->
  $ = require 'jquery'
  _ = require 'underscore'
  Backbone = require 'backbone'

  scroll_top_fast = ()  ->
    $('html, body').animate {scrollTop: 0}, 'fast'
  
  navigate_to_url = (url) ->
    if url.split('/')[0] == ''
      window.location = url
    else
      r = new Backbone.Router
      r.navigate url, trigger:true
    
  capitalize = (str) ->
    str.charAt(0).toUpperCase() + str.slice(1)

  handle_newlines = (str) ->
   str.replace(/(?:\r\n|\r|\n)/g, '<br />')
    

  start_application = (App) ->
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
    

  navbar_set_active = (path) ->
    path_top = path.split('/')[0]
    for li in $('#app-navbar li')
      liq = $ li
      liq.removeClass('active')
      if path_top == liq.attr('appname')
        liq.addClass('active')

  # FIXME: This can't be used
  # There needs to be a common stack
  # https://github.com/cloudchen/requirejs-bundle-examples
  make_component_paths = (components) ->
    paths =
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
    return paths
    
  module.exports =
    scroll_top_fast: scroll_top_fast
    navigate_to_url: navigate_to_url
    capitalize: capitalize
    handle_newlines: handle_newlines
    start_application: start_application
    navbar_set_active: navbar_set_active
    






