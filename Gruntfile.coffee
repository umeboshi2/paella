# Gruntfile for sitecontent

module.exports = (grunt) ->
  # variables to use in config
  # foo = 'bar'
  _ = require 'lodash'
  app_dir = 'javascripts'
    
  # config
  grunt.initConfig
    coffee:
      compile:
        options:
          bare: false
        expand: true
        src: ['**/*.coffee']
        dest: app_dir
        ext: '.js'
        cwd: 'coffee'
                
      compileWithMaps:
        options:
          bare: false
          sourceMap: true
        expand: true
        src: ['**/*.coffee']
        dest: app_dir
        ext: '.js'
        cwd: 'coffee'
        
    compass:
      compile:
        config: 'config.rb'
      watch:
        config: 'config.rb'
        watch: true
        quiet: false
        
        
    watch:
      coffee:
        files: ['coffee/**/*.coffee']
        tasks: ['coffee:compileWithMaps']
        options:
          spawn: false
      compass:
        files: ['sass/**/*.scss']
        tasks: ['compass:watch']
      buildjs:
        files: 'build.coffee'
        tasks: ['shell:compileBuildJS']

    concurrent:
      watchers:
        tasks: ['watch:coffee', 'watch:compass']
        options:
          logConcurrentOutput: true
        
    # from the docs
    changedFiles = Object.create null
    update_changedFiles = () ->
      grunt.config.set 'coffee.compileWithMaps.src', Object.keys changedFiles
      changedFiles = Object.create null
    onChange = _.debounce(update_changedFiles, 200)
      
    grunt.event.on 'watch', (action, filepath) ->
      #console.log "watch:->#{action} on #{filepath}"
      filepath = filepath.split('coffee/')[1]
      changedFiles[filepath] = action
      #console.log "files should equal -> #{Object.keys changedFiles}"
      onChange()
      
    clean:
      js:
        src: ['javascripts/**/*.js']
      emacs:
        src: ['**/*~']
        
    shell:
      bower:
        command: 'python scripts/prepare-bower-components.py'
        options:
          stdout: true

      compileBuildJS:
        command: 'python scripts/make-build-js.py'
        options:
          stdout: true
          
    # load grunt-* tasks
    require('matchdep').filterDev('grunt-*').forEach grunt.loadNpmTasks
    

    #grunt.event.on 'watch', (action, filepath, target) ->
    #  message = target + ': ' + filepath + ' has ' + action
    #  console.log message
    
    grunt.registerTask 'default', [
      'shell:bower'
      'coffee:compile'
      'compass:compile'
      'coffee:compileBuildJS'
      'coffee:compileWithMaps'
      ]

    grunt.registerTask 'watchers', [
      'concurrent:watchers'
      ]
