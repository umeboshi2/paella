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
  sidebar = renderable (model) ->
    div '.listview-list.btn-group-vertical', ->
      for entry in model.entries
        div '.btn.btn-default.' + entry.name, entry.label
        
  main_bumblr_view = renderable (model) ->
    p 'main bumblr view'

  bumblr_dashboard_view = renderable (model) ->
    p 'bumblr_dashboard_view'


  blog_dialog_view = renderable (blog) ->
    div '.modal-header', ->
      h2 'This is a modal!'
    div '.modal-body', ->
      p 'here is some content'
    div '.modal-footer', ->
      button '#modal-cancel-button.btn', 'cancel'
      button '#modal-ok-button.btn.btn-default', 'Ok'


  simple_blog_list = renderable () ->
    div ->
      a '.btn.btn-default', href:'#bumblr/addblog', "Add blog"
      div '#bloglist-container.listview-list'
      
  simple_blog_info = renderable (blog) ->
    div '.blog.listview-list-entry', ->
      a href:'#bumblr/viewblog/' + blog.name, blog.name
      #div "#delete-#{blog.name}.btn.btn-default", ->
      #  icon ".fa.fa-close"
      icon ".delete-blog-button.fa.fa-close.btn.btn-default.btn-xs",
      blog:blog.name
      
  simple_post_page_view = renderable () ->
    div '.mytoolbar.row', ->
      ul '.pager', ->
        li '.previous', ->
          icon '#prev-page-button.fa.fa-arrow-left.btn.btn-default'
        li ->
          icon '#slideshow-button.fa.fa-play.btn.btn-default'
        li '.next', ->
          icon '#next-page-button.fa.fa-arrow-right.btn.btn-default'
      #icon '#prev-page-button.fa.fa-arrow-left.btn.btn-default.pull-left'
      #icon '#slideshow-button.fa.fa-play.btn.btn-default'
    div '#posts-container.row'
      
  simple_post_view = renderable (post) ->
    div '.listview-list-entry', ->
      #p ->
      # a href:post.post_url, target:'_blank', post.blog_name
      span ->
        #for photo in post.photos
        photo = post.photos[0]
        current_width = 0
        current_size = null
        for size in photo.alt_sizes
          if size.width > current_width and size.width < 250
            current_size = size
            current_width = size.width
        size = current_size 
        a href:post.post_url, target:'_blank', ->
          img src:size.url

  new_blog_form_view = renderable (model) ->
    form_group_input_div
      input_id: 'input_blogname'
      label: 'Blog Name'
      input_attributes:
        name: 'blog_name'
        placeholder: ''
        value: 'dutch-and-flemish-painters'
    input '.btn.btn-default.btn-xs', type:'submit', value:'Add Blog'
        
  consumer_key_form = renderable (settings) ->
    form_group_input_div
      input_id: 'input_key'
      label: 'Consumer Key'
      input_attributes:
        name: 'consumer_key'
        placeholder: ''
        value: settings.consumer_key
    form_group_input_div
      input_id: 'input_secret'
      label: 'Consumer Secret'
      input_attributes:
        name: 'consumer_secret'
        placeholder: ''
        value: settings.consumer_secret
    form_group_input_div
      input_id: 'input_token'
      label: 'Token'
      input_attributes:
        name: 'token'
        placeholder: ''
        value: settings.token
    form_group_input_div
      input_id: 'input_tsecret'
      label: 'Token Secret'
      input_attributes:
        name: 'token_secret'
        placeholder: ''
        value: settings.token_secret
    input '.btn.btn-default.btn-xs', type:'submit', value:'Submit'
    
              
  module.exports =
    sidebar: sidebar
    main_bumblr_view: main_bumblr_view
    bumblr_dashboard_view: bumblr_dashboard_view
    blog_dialog_view: blog_dialog_view
    simple_blog_list: simple_blog_list
    simple_blog_info: simple_blog_info
    simple_post_view: simple_post_view
    simple_post_page_view: simple_post_page_view
    new_blog_form_view: new_blog_form_view
    consumer_key_form: consumer_key_form
    
    
