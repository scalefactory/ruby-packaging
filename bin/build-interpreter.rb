#!/usr/bin/ruby

require 'optparse'
require 'logger'
require 'yaml'
require 'fileutils'
require 'uri'
require 'net/http'
require 'erb'

class InterpreterBuilder

    class InterpreterBuilderTemplateBinding
        def initialize( config, source )
            @config, @source = config, source
        end

        def get_binding
            return binding()
        end
    end

    def initialize ( interpreter_version, options )
        @log = Logger.new( STDERR )
        @log.debug( "Starting #{self.class.name}.initialize" )
        @interpreter_version, @options = interpreter_version, options

        config_file = "conf/interpreters/#{interpreter_version}"

        begin
            @log.debug( "Opening #{config_file} as a yaml document" )
            file = File.open( config_file )
            @config = YAML::load( file ) 
        rescue => e
            @log.error "Could not open interpreter configuration file: #{e.message}"
            exit -1
        end

    end

    def create_tmp_build_tree ( base )

#        @tmpdir = "/tmp/interpreter-build-#{rand(100000)}"

        @basedir = base

        if ! FileTest.exists?( base ) 
            FileUtils.mkdir( base )
        end

        %w{BUILD RPMS SOURCES SPECS SRPMS}.each do |dir|
            to_create = "#{base}/#{dir}"
            if !FileTest.exist?( to_create ) 
                FileUtils.mkdir( to_create )
            else
                @log.debug( "#{to_create} already exists" )
            end
        end

    end

    def download_source

        @log.debug( "Downloading source from #{@config['source']}" )
        `wget -c -P #{@basedir}/SOURCES #{@config['source']}`

    end

    def template_spec_file

        version       = @config['version']
        source        = @config['source']
        buildrequires = @config['buildrequires'] || {}
        requires      = @config['requires']      || {}

        specfile = File.open( "#{@basedir}/SPECS/ruby#{version}.spec", 'w')

        erb = ERB.new( File.read( 'templates/interpreter.spec' ) )
        specfile.write( erb.result( binding() ) )
        specfile.close()

    end

    def build_rpm

        `rpmbuild -ba --define '_topdir #{@basedir}' #{@basedir}/SPECS/ruby#{@config['version']}.spec`

    end

    def go

        create_tmp_build_tree( '/tmp/build' )
        download_source
        template_spec_file
        build_rpm
        
    end

end

log = Logger.new( STDERR )

options = {}
OptionParser.new do |opts|

end.parse!

if ARGV.empty? 
   log.warn( "No interpreter versions given - nothing to do" ) 
end

ARGV.each do |interpreter_version|
    builder = InterpreterBuilder.new( interpreter_version, options )
    builder.go
end
