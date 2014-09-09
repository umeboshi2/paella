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
      
  simple_post_view = renderable (post) ->
    div '.alert.alert-success', ->
      p ->
        a href:post.post_url, target:'_blank', post.blog_name
      span ->
        #for photo in post.photos
        photo = post.photos[0]
        current_width = 0
        current_size = null
        for size in photo.alt_sizes
          if size.width > current_width and size.width < 600
            current_size = size
            current_width = size.width
        size = current_size 
        img src:size.url, href:post.url

  new_blog_form_view = renderable (model) ->
    div '.form-group', ->
      label '.control-label', for:'input_blogname', 'Blog Name'
      input '#input_blogname.form-control',
      name:'blog_name', dataValidation:'blog_name',
      placeholder:'', value: '8bitfuture'
    input '.btn.btn-default.btn-xs', type:'submit', value:'Add Blog'
    
  consumer_key_form = renderable (settings) ->
    div '.form-group', ->
      label '.control-label', for:'input_key', 'Consumer Key'
      input '#input_key.form-control',
      name:'consumer_key', dataValidation:'consumer_key',
      placeholder:'', value: settings.consumer_key
    div '.form-group', ->
      label '.control-label', for:'input_secret', 'Consumer Secret'
      input '#input_secret.form-control',
      name:'consumer_secret', dataValidation:'consumer_secret',
      placeholder:'', value: settings.consumer_secret
    div '.form-group', ->
      label '.control-label', for:'input_token', 'Token'
      input '#input_token.form-control',
      name:'token', dataValidation:'token',
      placeholder:'', value: settings.token
    div '.form-group', ->
      label '.control-label', for:'input_tsecret', 'Token Secret'
      input '#input_tsecret.form-control',
      name:'token_secret', dataValidation:'token_secret',
      placeholder:'', value: settings.token_secret
    input '.btn.btn-default.btn-xs', type:'submit', value:'Submit'
    
              
  module.exports =
    sidebar: sidebar
    main_bumblr_view: main_bumblr_view
    bumblr_dashboard_view: bumblr_dashboard_view
    simple_blog_list: simple_blog_list
    simple_blog_info: simple_blog_info
    simple_post_view: simple_post_view
    simple_post_page_view: simple_post_page_view
    new_blog_form_view: new_blog_form_view
    consumer_key_form: consumer_key_form
    
    
