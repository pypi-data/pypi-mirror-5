# Conventions
Jekyll and Hyde are both very flexible allowing end users to implement whatever
they would like. utterson utilizes that flexibility to impelemnt a website/blog
based on a specific set of conventions. The flexibilty of Jekyll and Hyde are 
sacrificed for the simplicity of utterson. This section details the conventions
that are utilized by utterson.

## Post Metadata
Jekyll and Hyde both provide post meta data. No metadata is required but some
items are expected for specific features to work. utterson adds some
conventions to the standard meta data. The following are the expected items.

```yaml
layout: <string>
title: <title>
summary: <string> # Used for the summary on the RSS feed.
date_posted: <string | YY-MM-DD> # None by default, updated by utterson 
								 # upon publishing.
date_updated: <string | YY-MM-DD> # None by default, updated by utterson 
								  # upon publishing and editing.
author: <string> # None by default. If user accounts are in use the user's 
				 # short name will be inserted on edit.
category: <string> # utterson will inject 'default' unless a category is 
                   # specified.
tags: [<string>,] # None by default. Tags may be added via utterson
scheduled_publish_date: <string | YY-MM-DD> # If the utterson daemon is 
											# running the post will be 
											# published at this time.
scheduled_publish_time: <string | HH:MM:SS UTC> # Default of none will 
												# publish at 12:00AM UTC. 
												# Otherwise the daemon will
												#  publish at the specified time.
include_fb_comments: <boolean> # Default of false. If true the template will
							   # insert facebook comments for the page. Template
							   # support is required.
```

## Directory Structure
Jekyll and Hyde provide a few conventions regarding the directory layout. To
support additional features utterson implements some additional conventions.

### Directory and File Layout
```
root # The root directory for utterson. Usually named after the site.
|- config.yml # utterson configuration file.
|- jekyll_root # The root directory all jekyll related files are stored in.
   |- _config.yml # Jekyll configuration file.
   |- **feed.xml** # Default RSS feeds.
   |- _posts
      |- **_drafts**
      |- **_templates**
      |- **_deleted**
   |- _site
   |- **_layouts**
   |- **_includes**
   |- **photos**
   |- css
```
### Directory Structure Adjustability
The directory structure does hae some adjustability. For example, the
jekyll_root may be located anywhere the user has read/write capabilites.
The config.yml file may be updated to specifiy the correct location. The 
config.yml file may also be located in a different directory than the
utterson exectuable is called from. The --config_file parameter allows
users to specify the config file.