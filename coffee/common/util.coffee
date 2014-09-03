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
        
  module.exports =
    scroll_top_fast: scroll_top_fast
    navigate_to_url: navigate_to_url
    capitalize: capitalize
    handle_newlines: handle_newlines
    start_application: start_application
    navbar_set_active: navbar_set_active
    






