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
    
  book_view = renderable (model) ->
    img '.book', src:model.thumbnail, alt:""

  bookstore_layout = renderable () ->
    div '#searchBar', ->
      text 'Search : '
      input '#searchTerm.form-control', type:'text', name:'search',
      autocomplete:'off', value:''
      icon '#spinner.fa.fa-spinner.fa-spin'
    div '#bookContainer'

  booklist_view = renderable () ->
    icon_button = '.btn.btn-default.btn-sm.fa'
    div style:'display:table;width:100%;height:100%;', ->
      div '.toolbar', ->
        icon "#{icon_button}.fa-arrow-left.pull-left"
        icon "#{icon_button}.fa-arrow-right.pull-right"
      div '.books'

  book_detail_view = renderable (book) ->
    a '#close-dialog.close', dataDissmiss:'modal', 'x'
    div '.imgBook', ->
      img src:book.thumbnail
    h1 book.title
    subtitle = if book?.subtitle then h2 book.subtitle else null
    description = if book?.description then p book.description else null
    href = "http://books.google.com/books?id=#{book.googleId}"
    subtitle
    description
    b 'Google link'
    a href:href, target:'_blank', href
    
    

  module.exports =
    frontdoor_main: frontdoor_main
    book_view: book_view
    bookstore_layout: bookstore_layout
    booklist_view: booklist_view
    book_detail_view: book_detail_view
    
    
    
