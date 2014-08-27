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
    
  

  module.exports =
    navigate_to_url: navigate_to_url
    capitalize: capitalize
    handle_newlines: handle_newlines
    






