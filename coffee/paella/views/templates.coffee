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
                    
                                        
    side_view_template = renderable () ->
        div '.main-content-manager-view.btn-group-vertical', ->
            div '.btn.btn-default.home-button', 'Main'
            div '.btn.btn-default.sitepaths-button', 'Paths'
            div '.btn.btn-default.sitetmpl-button', 'Templates'
            div '.btn.btn-default.sitecss-button', 'CSS'
            div '.btn.btn-default.sitejs-button', 'JS'
            div '.btn.btn-default.siteapp-button', 'App'
            
                        
    #######################################################
    entry_template = renderable (entry) ->
        div '.listview-list-entry', ->
            text entry.name
            div '.btn.btn-default.btn-xs.pull-right.show-entry-btn', ->
                icon '.fa.fa-pencil'
    #######################################################
    editor_template = renderable (model) ->
        div '#edit-status', ->
            text 'Editing ' + model.name
            div '#save-content.action-button', 'Save'
        div '#editor'
                
    listview_template = renderable (data) ->
        nbtn = '#new-entry-button.pull-right.btn.btn-default.btn-xs.add-entry-btn'                
        div '.listview-header', ->
            text list_titles[data.type]
            div nbtn, ->
                icon '.fa.fa-plus-square'
        div '.listview-list'
                
    create_template = renderable (model) ->
        _nameinput = '#nameinput.form-inline.form-control.pull-right'
        div '.create-form', ->
            div '#create-content.action-button', 'Save'
            span '.form-inline', style:'white-space:nowrap', ->
                label '.form-inline', for: 'nameinput', ->
                    text 'Name'
                input  _nameinput, style: 'width:80%', name: 'name'
            div '#edit-status'
            div '#editor'

    PageLayoutTemplate = renderable (user) ->
        div '.page', ->
            nav '.navbar.navbar-default.navbar-fixed-top.main-menu',\
            'data-spy':'affix', 'data-offset-top':'10', ->
                div '.navbar-header', ->
                    # the id for the data-target came from a tutorial
                    # and it should be renamed
                    button '.navbar-toggle', type:'button', 'data-toggle':'collapse',\
                    'data-target':'#ctx-menu-collapse-1', ->
                        span '.sr-only', 'Toggle navigations'
                        span 'badge', 'expand'
                    a '.navbar-brand', href:"#", 'brand'
                div '#ctx-menu-collapse-1.collapse.navbar-collapse', ->
                    div '.navbar.navbar-nav.navbar-right', ->
                        user_menu user
                    div '.nav.navbar-nav.navbar-left', ->
                        'raw main_menu'
            div '.main-content', ->
                div '.header.listview-header'
                div '.subheader'
                div '.two-col', ->
                    div '.sidebar'
                    div '.right-column-content'
                div '.footer'
            
    #######################################################
    module.exports =
        login_form:
            login_form
        side_view:
            side_view_template
        entry:
            entry_template
        editor:
            editor_template
        listview:
            listview_template
        create:
            create_template
        PageLayoutTemplate:
            PageLayoutTemplate
            
