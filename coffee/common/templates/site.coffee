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
  button, a, nav, form, small, section, 
  ul, li, b, h1, h2, aside, p,
  header} = teacup
            
    
  ########################################
  # Templates
  ########################################
  user_menu = renderable (user) ->
    name = user.username
    ul '#user-menu.ctx-menu.nav.navbar-nav', ->
      li '.dropdown', ->
        a '.dropdown-toggle', 'data-toggle':'dropdown', ->
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
            admin = false
            unless name == undefined
              groups = user.groups
              if groups != undefined
                for g in groups
                  if g.name == 'admin'
                    admin = true
            if admin
              li ->
                a href:'/admin', 'Administer Site'
            li ->
              a href:'/logout', 'Logout'

  ########################################
  main_bar = renderable () ->
    div '.navbar-header', ->
      button '.navbar-toggle', type:'button', 'data-toggle':'collapse',
      'data-target':'#mainbar-collapse', ->
        span '.sr-only', 'Toggle navigations'
        span 'badge', 'expand'
    div '#mainbar-collapse.collapse.navbar-collapse', ->
      div '#main-menu.nav.navbar-nav.navbar-left.main-menu'
      div '#user-menu.navbar.navbar-nav.navbar-right.main-menu'

  ########################################
  PageLayoutTemplateOrig = renderable (user) ->
    nav '#mainbar', 'data-spy':'affix', 'data-offset-top':'10'
    div '.page.container-fluid', ->
      div '#main-content', ->
        div '#header'
        div '#subheader'
        div '#content', ->
          div '.two-col.row', ->
            div '.sidebar.col-md-2'
            div '.right-column-content.col-md-10'
        div '#footer'

  PageLayoutTemplate = renderable () ->
    header ->
      div '.inner', ->
        h1 'Paella'
        h2 'Paella Automated Network Installer'
        a '.button', href:'https://github.com/umeboshi2/paella', ->
          small 'View project on'
          text 'GitHub'
    div '#content-wrapper', ->
      div '.inner.clearfix', ->
        section '#main-content', ->
          text 'This is a lot of text'
        aside '#sidebar', ->
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
              text 'is maintained by'
              a href:'https://github.com/umeboshi2', 'umeboshi2'

                  
          
            
  module.exports =
    PageLayoutTemplate: PageLayoutTemplate
    main_bar: main_bar
    user_menu: user_menu
    
      
