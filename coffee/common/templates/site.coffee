define (require, exports, module) ->
  $ = require 'jquery'
  _ = require 'underscore'
  Backbone = require 'backbone'
  teacup = require 'teacup'
  marked = require 'marked'
  
  renderable = teacup.renderable

  div = teacup.div
  # I use "icon" for font-awesome
  icon = teacup.i
  strong = teacup.strong
  span = teacup.span
  label = teacup.label
  input = teacup.input

  raw = teacup.raw
  text = teacup.text

  # Main Templates must use teacup.
  # The template must be a teacup.renderable, 
  # and accept a layout model as an argument.

  # Tagnames to be used in the template.
  {div, span, link, text, strong, label, input, 
  button, a, nav, form, small, section, 
  ul, li, b, h1, h2, aside, p,
  header} = teacup
            
    
  ########################################
  # Templates
  ########################################
  main_header = renderable () ->
    header ->
      div '.inner', ->
        h1 'Paella'
        h2 'Paella Automated Network Installer'
        a '.button', href:'https://github.com/umeboshi2/paella', ->
          small 'View project on'
          text 'GitHub'

  main_sidebar = renderable (model) ->
    ul '.sidebar-menu', ->
      for entry in model.entries
        li ->
          a href:entry.url, entry.name
    a '.button',
    href:'https://github.com/umeboshi2/paella/zipball/master', ->
      small 'Download'
      text '.zip file'
    a '.button',
    href:'https://github.com/umeboshi2/paella/tarball/master', ->
      small 'Download'
      text '.tar.gz file'
    p '.repo-owner', ->
      a href:'https://github.com/umeboshi2/paella', ->
        text 'is maintained by '
        a href:'https://github.com/umeboshi2', 'umeboshi2'

                  
  ########################################
  PageLayoutTemplate = renderable () ->
    div '#main-header', ->
      main_header()
    div '#content-wrapper', ->
      div '.inner.clearfix', ->
        section '#main-content'
        aside '#sidebar'
    div '#footer'
          
            
  module.exports =
    PageLayoutTemplate: PageLayoutTemplate
    main_header: main_header
    main_sidebar: main_sidebar
    
      
