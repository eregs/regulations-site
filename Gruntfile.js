'use strict';

module.exports = function(grunt) {

  grunt.initConfig({

    /**
     * Pull in the package.json file so we can read its metadata.
     */
    pkg: grunt.file.readJSON('package.json'),

    /**
     *
     *  Pull in environment-specific vars
     *
     */
    env: grunt.file.readJSON('config.json'),

    /**
     * Copy dependencies into static paths
     */
    copy: {
      main: {
        files: [
          {
            expand: true,
            flatten: true,
            src: ['node_modules/respond.js/dest/*'],
            dest: '<%= env.frontEndPath %>/js/built/lib/respond/',
            filter: 'isFile'
          }
        ]
      }
    },

    /**
     * https://github.com/gruntjs/grunt-contrib-sass
     */
    sass: {
        dev: {
            options: {
              style: 'expanded'
            },
            files: {
                '<%= env.frontEndPath %>/css/style.css': '<%= env.frontEndPath %>/css/scss/main.scss'
            }
        }
    },

    /**
     * CSSMin: https://github.com/gruntjs/grunt-contrib-cssmin
     *
     * Minify CSS for production
     */
    cssmin: {
      target: {
        files: {
          '<%= env.frontEndPath %>/css/regulations.min.css': ['<%= env.frontEndPath %>/css/style.css']
        }
      }
    },
    /**
     * ESLint: https://github.com/sindresorhus/grunt-eslint
     *
     * Validate files with ESLint.
     */
    eslint: {
        target: [
          'Gruntfile.js',
          '<%= env.frontEndPath %>/js/source/*.js',
          '<%= env.frontEndPath %>/js/source/events/**/*.js',
          '<%= env.frontEndPath %>/js/source/models/**/*.js',
          '<%= env.frontEndPath %>/js/source/views/**/*.js'
        ]
    },

    /**
    * Browserify:
    *
    * Require('modules') in the browser/bundle up dependencies.
    */
    browserify: {
      dev: {
        files: {
          '<%= env.frontEndPath %>/js/built/regulations.js': ['<%= env.frontEndPath %>/js/source/regulations.js','<%= env.frontEndPath %>/js/source/regulations.js']
        },
        options: {
          transform: ['babelify', 'browserify-shim'],
          browserifyOptions: {
            debug: true
          }
        }
      },
      dist: {
        files: {
          '<%= env.frontEndPath %>/js/built/regulations.min.js': ['<%= env.frontEndPath %>/js/source/regulations.js']
        },
        options: {
          transform: ['babelify', 'browserify-shim'],
          browserifyOptions: {
            debug: true
          },
          plugin: [
            [function(b) {
              b.plugin('minifyify', {
                map: '/static/regulations/js/built/regulations.min.map',
                output: grunt.template.process('<%= env.frontEndPath %>/js/built/regulations.min.map')
              });
            }]
          ]
        }
      }
    },

    mocha_istanbul: {
      coverage: {
        src: ['<%= env.frontEndPath %>/js/unittests/specs/**/*.js'],
        options: {
          root: '<%= env.frontEndPath %>/js',
          istanbulOptions: ['--include-all-sources'],
          coverageFolder: '<%= env.frontEndPath %>/js/unittests/coverage',
          excludes: [
            'built/**/*',
            'unittests/**/*',
            'source/otherlibs/**/*'
          ],
          coverage: false
        }
      }
     },

    shell: {
      'nose-chrome': {
        command: 'nosetests -s <%= env.testPath %> --tc=remote:chrome --tc=testUrl:<%= env.testUrl %>',
        options: {
            stdout: true,
            stderr: true
        }
      },

      'nose-ie11': {
        command: 'nosetests -s <%= env.testPath %> --tc=remote:ie11 --tc=testUrl:<%= env.testUrl %>',
        options: {
            stdout: true,
            stderr: true
        }
      }
    }
  });

  grunt.event.on('coverage', function( lcov, done ) {
    require('coveralls').handleInput( lcov, function( err ) {
      if ( err ) {
        return done( err );
      }
      done();
    });
  });
  /**
   * The above tasks are loaded here.
   */
  require('load-grunt-tasks')(grunt);

  /**
   * Create task aliases by registering new tasks
   */
  grunt.registerTask('nose', ['shell:nose-chrome', 'shell:nose-ie11']);
  grunt.registerTask('test', ['eslint', 'mocha_istanbul', 'nose']);
  grunt.registerTask('test-js', ['eslint', 'mocha_istanbul']);
  grunt.registerTask('build-dev', ['copy', 'browserify:dev', 'sass']);
  grunt.registerTask('build-dist', ['copy', 'browserify:dist', 'sass', 'cssmin']);
  grunt.registerTask('default', ['build-dist']);
};
