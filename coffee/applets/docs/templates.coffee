# modular template loading
define (require, exports, module) ->
  $ = require 'jquery'
  _ = require 'underscore'
  Backbone = require 'backbone'
  teacup = require 'teacup'
  marked = require 'marked'
  
  renderable = teacup.renderable
  raw = teacup.raw
  
  # I use "icon" for font-awesome
  icon = teacup.i
  text = teacup.text
  # Main Templates must use teacup.
  # The template must be a teacup.renderable, 
  # and accept a layout model as an argument.

  # Tagnames to be used in the template.
  {div, span, link, strong, label, input, img, textarea
  button, a, nav, form, p,
  ul, li, b,
  h1, h2, h3,
  subtitle, section, hr
  } = teacup
            
    
  ########################################
  # Templates
  ########################################
  frontdoor_main = renderable (page) ->
    raw marked page.content
    
              
  page_list_entry = renderable (page) ->
    div '.listview-list-entry', ->
      span '.btn-default.btn-xs', ->
        a href:'#docs/editpage/' + page.id,
        style:'color:black', ->
          icon '.edit-page.fa.fa-pencil'
      text "    " 
      a href:'#docs/showpage/' + page.id, page.id
        
  page_list = renderable () ->
    div '.listview-header', ->
      text 'Documents'
      span '#add-new-page-button.btn.btn-default.btn-xs.pull-right', 'New Page'
    div '.listview-list'

  show_page_view = renderable (page) ->
    div '.listview-header', ->
      text page.name
    div '.listview-list', ->
      teacup.raw marked page.content
      
  edit_page = renderable (page) ->
    div '.listview-header', ->
      text "Editing " + page.id
      div '#save-button.pull-left.btn.btn-default.btn-xs', ->
        text 'save'
    div '#editor'

  module.exports =
    frontdoor_main: frontdoor_main
    page_list_entry: page_list_entry
    page_list: page_list
    show_page_view: show_page_view
    edit_page: edit_page
    new_page_form: new_page_form
    
    
