# modular template loading
define (require, exports, module) ->
  $ = require 'jquery'
  _ = require 'underscore'
  Backbone = require 'backbone'
  teacup = require 'teacup'
  marked = require 'marked'
  
  renderable = teacup.renderable
  raw = teacup.raw
  
  div = teacup.div
  # I use "icon" for font-awesome
  icon = teacup.i
  strong = teacup.strong
  span = teacup.span
  label = teacup.label
  input = teacup.input
  textarea = teacup.textarea
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
            
    
  ########################################
  # Templates
  ########################################
  jellyfish = renderable () ->
    div 'listview-header', ->
      text 'Jelly fish content'
      
  page_list_entry = renderable (page) ->
    div '.listview-list-entry', ->
      span '.btn-default.btn-xs', ->
        a href:'#sitetext/editpage/' + page.id,
        style:'color:black', ->
          icon '.edit-page.fa.fa-pencil'
      text "    "
      a href:'#sitetext/showpage/' + page.id, page.name
        
      
  page_list = renderable () ->
    div '.listview-header', 'Wiki Pages'
    div '.listview-list'

  page_view = renderable (page) ->
    div '.listview-header', ->
      text page.name
    div '.listview-list', ->
      teacup.raw marked page.content
      
  edit_page = renderable (page) ->
    div '.listview-header', ->
      text "Editing " + page.name
      div '#save-button.pull-left.btn.btn-default.btn-xs', ->
        text 'save'
    div '#editor'
    

  new_page_form = renderable () ->
    div '.form-group', ->
      label '.control-label', for:'input_name', 'Page Name'
      input '#input_name.form-control',
      name:'name', 'data-validation':'name',
      placeholder:'New Page', value:''
    div '.form-group', ->
      label '.control-label', for:'input_content', 'Content'
      textarea '#input_content.form-control',
      name:'content', 'data-validation':'content',
      placeholder:'...add text....', value:''
    input '.btn.btn-default.btn-xs', type:'submit', value:'Add Page'
    
  module.exports =
    jellyfish: jellyfish
    page_list_entry: page_list_entry
    page_list: page_list
    page_view: page_view
    edit_page: edit_page
    new_page_form: new_page_form
    
    