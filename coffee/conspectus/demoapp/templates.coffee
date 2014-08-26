# modular template loading
define (require, exports, module) ->
  $ = require 'jquery'
  _ = require 'underscore'
  Backbone = require 'backbone'

  marked = require 'marked'
  
  teacup = require 'teacup'

  renderable = teacup.renderable

  div = teacup.div
  # I use "icon" for font-awesome
  icon = teacup.i
  strong = teacup.strong
  span = teacup.span
  label = teacup.label
  input = teacup.input

  text = teacup.text
  img = teacup.img
  # Main Templates must use teacup.
  # The template must be a teacup.renderable, 
  # and accept a layout model as an argument.

  # Tagnames to be used in the template.
  {div, span, link, text, strong, label, input, 
  button, a, nav, form, p,
  ul, li, b,
  h1, h2, h3,
  subtitle, section, hr
  } = teacup

  # FIXME: add to util model            
  capitalize = (str) ->
    str.charAt(0).toUpperCase() + str.slice(1)

  # FIXME: add to util model            
  handle_newlines = renderable (str) ->
   str.replace(/(?:\r\n|\r|\n)/g, '<br />')
    
  ########################################
  # Templates
  ########################################
  sidebar = renderable (model) ->
    div '.listview-list.btn-group-vertical', ->
      for entry in model.entries
        div '.btn.btn-default.' + entry.name, entry.label
        
  ##################################################################
  # ##########################
  ##################################################################    
          
  module.exports =
    sidebar: sidebar
