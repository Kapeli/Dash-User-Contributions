require 'rubygems'
require 'mechanize'
require 'sqlite3'

EXTRACT_GLEXT_PAGE   = "http://www.opengl.org/registry/"
EXTRACT_GLEXT_DB     = "../docSet.dsidx"

a = Mechanize.new { |agent|
  agent.user_agent_alias = 'Mac Safari'
}

# Remove any previous files.
if File.exists? EXTRACT_GLEXT_DB
    File.unlink EXTRACT_GLEXT_DB
end

# Create sqlite db.
db = SQLite3::Database.new(EXTRACT_GLEXT_DB)
db.execute "CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);"
db.execute "CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);"

a.get(EXTRACT_GLEXT_PAGE) do |page|

    # Grab all links on this page.
    page_links = page.links

    # Go through all links
    page_links.each do |link|

        # Only consider extensions links.
        if link.to_s =~ /^GL_/ || link.to_s =~ /^GLX_/ || link.to_s =~ /^WGL_/
            
            # Construct file name.
            link_file = "#{link.to_s}.txt"

            # See if we need to remove previous file.
            if File.exist? link_file
                File.delete link_file
            end

            # Grab corresponding file.
            a.get(EXTRACT_GLEXT_PAGE + "/#{link.uri.to_s}").save_as link_file

            # Insert into db.
            db.execute "INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES ('#{link.to_s}', 'Entry', '#{link_file}');"
        end
    end
end

db.close
