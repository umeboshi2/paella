# modular template loading
define (require, exports, module) ->
  $ = require 'jquery'
  _ = require 'underscore'
  Backbone = require 'backbone'
  teacup = require 'teacup'
  marked = require 'marked'

  { name_content_form } = require 'common/templates'
  
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
  subtitle, section, hr,
  table, tr, td,
  select, option,
  } = teacup
            
    
  { form_group_input_div } = require 'common/templates'

  { capitalize } = require 'common/util'
  
  ########################################
  # Templates
  ########################################
  frontdoor_main = renderable (page) ->
    raw marked page.content

  _listview_header = renderable (label) ->
    div '.listview-header', "#{label}"

  _recipe_option = renderable (machine, attribute) ->
    label = '<No Recipe>'
    if attribute not of machine
      option selected: null, label
    else
      option label
      
  _select_input = renderable (machine, attribute, optionlist, label, title) ->
    div '.input-group', ->
      span '.input-group-addon', label
      select "##{attribute}.selectpicker.form-control", dataLiveSearch:'true',
      title:title, ->
        if attribute in ['recipe', 'raid_recipe']
          _recipe_option machine, attribute
        for opt in optionlist
          if attribute of machine and machine[attribute] == opt
            option selected: null, opt
          else
            option opt
            
      
  machine_name_entry = renderable (model) ->
    div '.listview-list-entry.machine', ->
      a href: '#machines/viewmachine/' + model.name, model.name
      
  simple_machine_list = renderable () ->
    _listview_header 'Machines'
    div '.listview-list'

  view_machine_orig = renderable (machine) ->
    div ->
      text machine.name
    div ->
      text machine.uuid
    
  _set_install_button = renderable (machine) ->
    bmain = '#set-install-button.btn.btn-default.btn-xs'
    verb = 'Set'
    bvalue = 'set'
    if machine.pxeconfig
      verb = 'Remove'
      bvalue = 'remove'
    div bmain, bvalue: bvalue, ->
      text "#{verb} #{machine.name} for install."
      
  view_machine = renderable (machine) ->
    archs = ['amd64', 'i386']
    ostypes = ['debian', 'mswindows']
    _set_install_button machine
    div '.listview-header', ->
      div machine.name
      div machine.uuid
    div '.listview-list', ->
      _select_input machine, 'arch', archs, 'Arch:', 'Select an architecture.'
      _select_input machine, 'ostype', ostypes, 'OS Type:', 'Select an operating system.'
      _select_input machine, 'recipe', machine.all_recipes, 'Partition Recipe',
      'Select a partition recipe.'
      _select_input machine, 'raid_recipe', machine.all_raid_recipes, 'Raid Recipe',
      'Select a raid recipe.'
      form_group_input_div
        input_id: 'input_iface'
        label: 'Network Interface for Install'
        input_attributes:
          name: 'iface'
          placeholder: ''
          value: machine.iface
      div '#update-machine-button.btn.btn-default.btn-sm', 'Update Machine'
    
  edit_recipe = renderable (recipe) ->
    div '.listview-header', ->
      text "Recipe: #{recipe.name}"
      div '#save-button.pull-left.btn.btn-default.btn-xs', ->
        text 'save'
    div '#editor'
    console.log 'recipe', recipe

  module.exports =
    frontdoor_main: frontdoor_main
    machine_name_entry: machine_name_entry
    simple_machine_list: simple_machine_list
    view_machine: view_machine
