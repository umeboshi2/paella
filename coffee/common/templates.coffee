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
  form_group_input_div = renderable (data) ->
    div '.form-group', ->
      label '.control-label',
        for:data.input_id
        data.label
      input_type = if data?.input_type then data.input_type else input
      input_type "##{data.input_id}.form-control", data.input_attributes
          
  login_form = renderable (user) ->
    form
      role:'form'
      method: 'POST'
      action: '/login', ->
        form_group_input_div
          input_id: 'input_username'
          label: 'User Name'
          input_attributes:
            name: 'username'
            placeholder: 'User Name'
        form_group_input_div
          input_id: 'input_password'
          label: 'Password'
          input_attributes:
            name: 'password'
            type: 'password'
            placeholder: 'Type your password here....'
        button '.btn.btn-default', type:'submit', 'login'
        
  ########################################
  user_menu = renderable (user) ->
    name = user.username
    ul '#user-menu.ctx-menu.nav.navbar-nav', ->
      li '.dropdown', ->
        a '.dropdown-toggle', dataToggle:'dropdown', ->
          if name == undefined
            text "Guest"
          else
            text name
          b '.caret'
        ul '.dropdown-menu', ->
          if name == undefined
            li ->
              a href:'/login', 'login'
          else
            li ->
              a href:'/app/user', 'User Page'
            # we need a "get user info" from server
            # to populate this menu with 'admin' link
            # FIXME use "?." to help here
            admin = false
            unless name == undefined
              groups = user.groups
              if groups != undefined
                for g in groups
                  if g.name == 'admin'
                    admin = true
            if admin
              li ->
                href = '/admin'
                pathname = window.location.pathname
                if pathname.split(href)[0] == ''
                  href = '#'
                a href:href, 'Administer Site'
            li ->
              a href:'/logout', 'Logout'

  ########################################
  BootstrapNavBarTemplate = renderable (appmodel) ->
    div '.container', ->
      div '#navbar-brand.navbar-header', ->
        button '.navbar-toggle', type:'button', dataToggle:'collapse',
        dataTarget:'.navbar-collapse', ->
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
        ul '#main-menu.nav.navbar-nav.navbar-left'
        ul '#user-menu.nav.navbar-nav.navbar-right'
              

  ########################################
  BootstrapLayoutTemplate = renderable () ->
    div '#modal'
    div '#main-navbar.navbar.navbar-default.navbar-fixed-top',
    role:'navigation'
    #div '#header.listview-header'
    div '.container-fluid', ->
      div '.row', ->
        div '#sidebar.col-sm-2'
        div '#main-content.col-sm-9'
        
    div '#footer'
    
  BootstrapNoGridLayoutTemplate = renderable () ->
    div '#main-navbar.navbar.navbar-default.navbar-fixed-top',
    role:'navigation'
    #div '#header.listview-header'
    div '.main-layout', ->
      div '#sidebar'
      div '#main-content'
        
    div '#footer'
    
  ########################################
  main_sidebar = renderable (model) ->
    div '.sidebar-menu', ->
      for entry in model.entries
        div '.sidebar-entry-button', buttonUrl:entry.url, ->
          text entry.name          
  

  ########################################
  module.exports =
    form_group_input_div: form_group_input_div
    login_form: login_form
    user_menu: user_menu
    BootstrapNavBarTemplate: BootstrapNavBarTemplate
    BootstrapLayoutTemplate: BootstrapLayoutTemplate
    BootstrapNoGridLayoutTemplate: BootstrapNoGridLayoutTemplate
    main_sidebar: main_sidebar
