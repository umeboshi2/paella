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
  subtitle, section, hr
  } = teacup
            
    
  { form_group_input_div } = require 'common/templates'

  { capitalize } = require 'common/util'
  
  ########################################
  # Templates
  ########################################
  frontdoor_main = renderable (page) ->
    raw marked page.content

  _recipe_header = renderable (label) ->
    div '.listview-header', "#{label}"
      
  recipe_name_entry = renderable (model) ->
    div '.listview-list-entry.recipe', ->
      a href: '#diskrecipes/viewrecipe/' + model.name, model.name

  raid_recipe_name_entry = renderable (model) ->
    div '.listview-list-entry.recipe', ->
      a href: '#diskrecipes/viewraid/' + model.name, model.name

  simple_recipe_list = renderable () ->
    _recipe_header 'Partition Recipes'
    div '.listview-list'

  simple_raid_recipe_list = renderable () ->
    _recipe_header 'Raid Recipes'
    div '.listview-list'
    
    
  edit_recipe = renderable (recipe) ->
    div '.listview-header', ->
      text "Recipe: #{recipe.name}"
      div '#save-button.pull-left.btn.btn-default.btn-xs', ->
        text 'save'
    div '#editor'
    console.log 'recipe', recipe

  new_recipe_form = renderable (recipe) ->
    _recipe_header 'New Recipe'
    div '.listview-list', ->
      name_content_form recipe

  new_raid_recipe_form = renderable (recipe) ->
    _recipe_header "New Raid Recipe"
    div '.listview-list', ->
      name_content_form recipe

  module.exports =
    frontdoor_main: frontdoor_main
    recipe_name_entry: recipe_name_entry
    raid_recipe_name_entry: raid_recipe_name_entry
    simple_recipe_list: simple_recipe_list
    simple_raid_recipe_list: simple_raid_recipe_list
    edit_recipe: edit_recipe
    new_recipe_form: new_recipe_form
    new_raid_recipe_form: new_raid_recipe_form
    
