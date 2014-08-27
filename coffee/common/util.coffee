define (require, exports, module) ->
  $ = require 'jquery'
  _ = require 'underscore'
  Backbone = require 'backbone'

  navigate_to_url = (url) ->
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
    
      
      

  module.exports =
    navigate_to_url: navigate_to_url
    capitalize: capitalize
    handle_newlines: handle_newlines
    start_application: start_application







