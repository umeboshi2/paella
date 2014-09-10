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
            
  { form_group_input_div } = require 'common/templates'

  ########################################
  # Templates
  ########################################
  page_list_entry = renderable (page) ->
    div '.listview-list-entry', ->
      span '.btn-default.btn-xs', ->
        a href:"#sitetext/editpage/#{page.name}",
        style:'color:black', ->
          icon '.edit-page.fa.fa-pencil'
      text "    "
      a href:"#sitetext/showpage/#{page.name}", page.name
        
      
  page_list = renderable () ->
    div '.listview-header', 'Wiki Pages'
    div '.listview-list'

  page_view = renderable (page) ->
    div '.listview-header', ->
      text page.name
    div '.listview-list', ->
      teacup.raw marked page?.content
      
  edit_page = renderable (page) ->
    div '.listview-header', ->
      text "Editing #{page.name}"
      div '#save-button.pull-left.btn.btn-default.btn-xs', ->
        text 'save'
    div '#editor'
    

  new_page_form = renderable () ->
    form_group_input_div
      input_id: 'input_name'
      label: 'Page Name'
      input_attributes:
        name: 'name'
        placeholder: 'New Page'
    form_group_input_div
      input_id: 'input_content'
      input_type: textarea
      label: 'Content'
      input_attributes:
        name: 'content'
        placeholder: '...add some text....'
    input '.btn.btn-default.btn-xs', type:'submit', value:'Add Page'
        
  module.exports =
    page_list_entry: page_list_entry
    page_list: page_list
    page_view: page_view
    edit_page: edit_page
    new_page_form: new_page_form
    
    
