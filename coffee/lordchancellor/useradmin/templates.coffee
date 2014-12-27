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
  simple_user_entry = renderable (model) ->
    div '.listview-list-entry', ->
      a href:'#useradmin/viewuser/' + model.id, model.name

  simple_group_entry = renderable (model) ->
    div '.listview-list-entry', ->
      a href:'#useradmin/viewgroup/' + model.id, model.name

  simple_user_list = renderable (users) ->
    div '.listview-header', 'Users'
    div '.listview-list'
    
  simple_group_list = renderable (groups) ->
    div '.listview-header', 'Groups'
    div '.listview-list'


  view_user_page = renderable (model) ->
    div ->
      div '.listview-header', model.name
      p ->
        text "This is the user page for #{model.name}"
      hr
      div '.btn.btn-default.delete-user-button', 'Delete User'


  new_user_form = renderable () ->
    form_group_input_div
      input_id: 'input_name'
      label: 'User Name'
      input_attributes:
        name: 'name'
        placeholder: 'User Name'
    form_group_input_div
      input_id: 'input_password'
      label: 'Password'
      input_attributes:
        name: 'password'
        type: 'password'
        placeholder: 'Enter password'
    form_group_input_div
      input_id: 'input_confirm'
      label: 'Confirm Password'
      input_attributes:
        name: 'confirm'
        type: 'password'
        placeholder: 'Confirm your password'
    input '.btn.btn-default.btn-xs', type:'submit', value:"Add New User"
      
  new_group_form = renderable () ->
    form_group_input_div
      input_id: 'input_name'
      label: 'Group Name'
      input_attributes:
        name: 'name'
        placeholder: 'Enter group name'
    input '.btn.btn-default.btn-xs', type:'submit', value:"Add New Group"

    
         
  module.exports =
    simple_user_entry: simple_user_entry
    simple_group_entry: simple_group_entry
    simple_user_list: simple_user_list
    simple_group_list: simple_group_list
    new_user_form: new_user_form
    new_group_form: new_group_form
    view_user_page: view_user_page
    
