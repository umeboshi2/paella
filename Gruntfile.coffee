# Gruntfile for sitecontent

module.exports = (grunt) ->
  # variables to use in config
  # foo = 'bar'
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
        
      compileBuildJS:
        options:
          bare: true
        src: 'build.coffee'
        dest: 'build.js'
        
        
    compass:
      compile:
        config: 'config.rb'
        
    watch:
      coffee:
        files: ['coffee/**/*.coffee']
        tasks: ['coffee:compileWithMaps']
      compass:
        files: ['sass/**/*.scss']
        tasks: ['compass']
      buildjs:
        files: 'build.coffee'
        tasks: ['coffee:compileBuildJS']
        
    copy:
      coffee:
        files:
          [
            expand: true
            src: ['**/*.coffee']
            dest: 'javascripts/'
            cwd: 'coffee'
          ]  
        
        
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
        
    # load grunt-* tasks
    require('matchdep').filterDev('grunt-*').forEach grunt.loadNpmTasks
    
    grunt.registerTask 'default', [
      'shell:bower'
      'coffee:compile'
      'compass:compile'
      'coffee:compileBuildJS'
      'coffee:compileWithMaps'
      ]
                          
        