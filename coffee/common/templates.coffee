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
  login_form = renderable (user) ->
    form role:'form', method:'POST',
    action:'/login', ->
      div '.form-group', ->
        label for:'input_username', 'User Name'
        input '#input_username.form-control',
        name: 'username',
        placeholder:"User Name"
      div '.form-group', ->
        label for:'input_password', 'Password'
        input '#input_password.form-control',
        name: 'password',
        type:'password', placeholder:'password'
      button '.btn.btn-default', type:'submit', 'login'
                    
                  
  ########################################
  BootstrapNavBarTemplate = renderable (appmodel) ->
    div '.container', ->
      div '#navbar-brand.navbar-header', ->
        button '.navbar-toggle', type:'button', 'data-toggle':'collapse',
        'data-target':'.navbar-collapse', ->
          span '.sr-only', 'Toggle Navigation'
          span '.icon-bar'
          span '.icon-bar'
          span '.icon-bar'
        a '.navbar-brand', href:appmodel.brand.url, appmodel.brand.name
      div '.navbar-collapse.collapse', ->
        ul '#app-navbar.nav.navbar-nav', ->
          for app in appmodel.apps
            li appname:app.appname, ->
              a href:app.url, app.name
        ul '.nav.navbar-nav.navbar-right', ->
              

  BootstrapLayoutTemplate = renderable () ->
    div '#main-navbar.navbar.navbar-default.navbar-fixed-top',
    role:'navigation'
    div '.container-fluid', ->
      div '.row', ->
        div '#sidebar.col-sm-2'
        div '#main-content.col-sm-9'
        
    div '#footer'
    

  main_sidebar = renderable (model) ->
    div '.sidebar-menu', ->
      for entry in model.entries
        div '.sidebar-entry-button', 'button-url':entry.url, ->
          text entry.name          
  

  module.exports =
    login_form: login_form
    BootstrapLayoutTemplate: BootstrapLayoutTemplate
    BootstrapNavBarTemplate: BootstrapNavBarTemplate
    main_sidebar: main_sidebar












