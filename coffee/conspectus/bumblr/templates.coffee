# modular template loading
define (require, exports, module) ->
  $ = require 'jquery'
  _ = require 'underscore'
  Backbone = require 'backbone'

  marked = require 'marked'
  
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
            
  capitalize = (str) ->
    str.charAt(0).toUpperCase() + str.slice(1)

  handle_newlines = (str) ->
   str.replace(/(?:\r\n|\r|\n)/g, '<br />')
    
  ########################################
  # Templates
  ########################################
  sidebar = renderable (model) ->
    div '.listview-list.btn-group-vertical', ->
      for entry in model.entries
        div '.btn.btn-default.' + entry.name, entry.label
        
  main_bumblr_view = renderable (model) ->
    p 'main bumblr view'

  bumblr_dashboard_view = renderable (model) ->
    p 'bumblr_dashboard_view'


  simple_blog_list = renderable () ->
    div ->
      a '.btn.btn-default', href:'#bumblr/addblog', "Add blog"
      div '#bloglist-container'
      
  simple_blog_info = renderable (blog) ->
    div ->
      a href:'#bumblr/viewblog/' + blog.name, blog.name

  simple_post_page_view = renderable () ->
    div '#posts-container', ->
      div '.mytoolbar', ->
        div '#prev-page-button.btn.btn-default.pull-left', '<-'
        div '#next-page-button.btn.btn-default.pull-right', '->'
      #div '#posts-container'
      
  simple_post_view = renderable (post) ->
    div '.alert.alert-success', ->
      p ->
        a href:post.post_url, target:'_blank', post.blog_name
      span ->
        #for photo in post.photos
        photo = post.photos[0]
        for size in photo.alt_sizes
          if size.width == 250
            img src:size.url, href:post.url

  new_blog_form_view = renderable (model) ->
    div '.form-group', ->
      label '.control-label', for:'input_blogname', 'Blog Name'
      input '#input_blogname.form-control',
      name:'blog_name', 'data-validation':'blog_name',
      placeholder:'', value: '8bitfuture'
    input '.btn.btn-default.btn-xs', type:'submit', value:'Add Blog'
    
  consumer_key_form = renderable (settings) ->
    div '.form-group', ->
      label '.control-label', for:'input_key', 'Consumer Key'
      input '#input_key.form-control',
      name:'consumer_key', 'data-validation':'consumer_key',
      placeholder:'', value: settings.consumer_key
    div '.form-group', ->
      label '.control-label', for:'input_secret', 'Consumer Secret'
      input '#input_secret.form-control',
      name:'consumer_secret', 'data-validation':'consumer_secret',
      placeholder:'', value: settings.consumer_secret
    div '.form-group', ->
      label '.control-label', for:'input_token', 'Token'
      input '#input_token.form-control',
      name:'token', 'data-validation':'token',
      placeholder:'', value: settings.token
    div '.form-group', ->
      label '.control-label', for:'input_tsecret', 'Token Secret'
      input '#input_tsecret.form-control',
      name:'token_secret', 'data-validation':'token_secret',
      placeholder:'', value: settings.token_secret
    input '.btn.btn-default.btn-xs', type:'submit', value:'Submit'
    
        
  ##################################################################
  # ##########################
  ##################################################################    
          
  module.exports =
    sidebar: sidebar
    main_bumblr_view: main_bumblr_view
    bumblr_dashboard_view: bumblr_dashboard_view
    simple_blog_list: simple_blog_list
    simple_blog_info: simple_blog_info
    simple_post_view: simple_post_view
    simple_post_page_view: simple_post_page_view
    new_blog_form_view: new_blog_form_view
    
    