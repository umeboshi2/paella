define (require, exports, module) ->
    $ = require 'jquery'
    _ = require 'underscore'
    Backbone = require 'backbone'
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

    # Main Templates must use teacup.
    # The template must be a teacup.renderable, 
    # and accept a layout model as an argument.

    # Tagnames to be used in the template.
    {div, span, link, text, strong, label, input, 
    button, a, nav, form,
    ul, li, b} = teacup
            
    
    ########################################
    # Templates
    ########################################
    make_menu = renderable (model) ->
      cls = '.' + model.tagclass + '.ctx-menu.nav.navbar.navbar-nav'
      ul cls, ->
        li '.dropdown', ->
          a '.dropdown-toggle', 'data-toggle':'dropdown', ->
            text model.label
            b '.caret'
          ul '.dropdown-menu', ->
            for entry in model.entries
              li ->
                a href:entry.url, entry.name
    module.exports =
      make_menu: make_menu
      
    
    