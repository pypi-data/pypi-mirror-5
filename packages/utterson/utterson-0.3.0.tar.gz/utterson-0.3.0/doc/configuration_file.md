# Configuration File
Utterson contains a single core configuration file. The file may be generated
three ways. With the -generate_config switch, the -build_utterson
switch, and manually.

## Raw File
```yaml
site:
  url: <string>
  deployment:
    root: <string>
    method: <string>
  jekyll_root: <string>
  site_title: <string>

tags:
  - default

categories:
  - default

users:
```

## Configuration Parameter Definitions
- site
 - **url**: The full url for the site when published.
 - **deployment**
  - **root**: The root location the site should be copied after building.
  - **method**: [rsync_ssh, rsync, cp]
 - **jekyll_root**: The root to the jekyll site.
 - **site_title**: The sites title.
