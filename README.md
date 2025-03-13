# Linkding Bookmarks Manager

A Docker container management script for running multiple instances of the [linkding](https://github.com/sissbruecker/linkding) bookmark manager.  Includes customizable title, logo and color theme.

## Installation

**Current Release:  v1.0.0**

1. Clone this repository:
```bash
cd /opt
git clone --branch v1.0.0 https://git.ucommandit.org/uci/uci-linkding-bookmarks.git bookmarks
cd bookmarks
```
or

```bash
cd /opt
git clone --branch v1.0.0 https://github.com/uCOMmandIt/uci-linkding-bookmarks.git bookmarks
cd bookmarks
```
> For latest development version, omit the `--branch v1.0.0` option

> **Quick Start for CSS Only:**  
> If you just want to generate custom CSS for an existing linkding instance:
> ```bash
> ./bm css anyname   # Generates CSS files for copy/paste into linkding settings
> ```
> see the [Customization](#customization) section below.

2. Create a branch for your machine:
```bash
git checkout -b my-machine-name
```

3. Edit .gitignore to track your configurations:
```bash
# Remove or comment out these lines:
# /assets/custom-logo.*
# /containers/*
```

4. Start a new bookmarks container:
```bash
./bm run mybookmarks
```

> On first run, you'll be prompted to:
> - Set custom port (or auto-detect available)
> - Configure data storage location
> - Set admin username/password

5. Running ok?  Commit your branch:
```bash
git add .
git commit -m "feat: add first bookmarks configuration/instance"
[ create a remote repo, set the remote]
git push myremote my-machine-name
```

> **Data Storage Note:**  
> By default, bookmark data in `bookmarks/` is not committed (recommended).  
> To version control your bookmarks, either:
> - Remove `bookmarks/` from .gitignore (not recommended)
> - Use `HOST_VOLUME_DIR` to store data in a backed-up location (recommended)


6. Customize your theme and title after the site is up and running:
```bash
./bm css mybookmarks
```
see the [Customization](#customization) section below.

## Features

- Manage multiple bookmark containers on the same machine
- Automatic port conflict detection and resolution
- Environment variable persistence
- Volume management for persistent data
- Custom logo and theme support

## Usage

```bash
bm <command> [options] <bookmarks-name>
```

### Commands requiring bookmarks name:
- `run`      Create and start the bookmarks container interactively
- `start`    Start container in detached mode (same as: run -d)
- `stop`     Stop the running bookmarks container
- `restart`  Restart the bookmarks container
- `log`      Show logs from the bookmarks container
- `config`   Display the Docker Compose configuration
    - `-e`   EditConfigure environment variables (port, paths, credentials)
- `admin`    Run commands in the container:
    - `-s`        Open an interactive shell
    - `-x`        Execute a shell command
    - `[args]`    Run Django manage.py commands (default)
- `delete`   Delete container, environment file and data (DANGEROUS!)

### Commands with optional bookmarks name:
- `status`   Show status of all instances or specific instance
    -  `-q` Quiet mode - only output running instance names

### Commands that don't use bookmarks name:
- `upgrade`  Upgrade all instances to latest linkding version
- `help`     Show this help message

### Examples
```bash
bm run mybookmarks          # Create and start container interactively
bm run -d mybookmarks      # Create and start container in background
bm start mybookmarks       # Start container in background
bm stop mybookmarks        # Stop the container
bm status                  # Show all instances status
bm status -q              # List running instances (for scripts)
bm status mybookmarks     # Check specific instance status
bm upgrade               # Upgrade all instances to latest version
```

## Environment Variables - Configuration

Each instance/container gets a corresponding <name>.env in /containers

`./bm config -e` will allow you to run the configurator (recommended) or edit the file directly.

Basic settings configured through `bm config -e`:
- `HOST_PORT` - Container port (default: 9090)
- `HOST_VOLUME_DIR` - Base data directory
- `HOST_VOLUME_PATH` - Full custom data path
- `LD_SUPERUSER_NAME` - Admin username
- `LD_SUPERUSER_PASSWORD` - Admin password

Additional Linkding options can be added manually to the env file. See `example.env` for available settings such as:
- Context path
- Authentication proxy support
- URL validation
- Background tasks
- CSRF trusted origins

For full documentation of options, see [Linkding Options](https://linkding.link/options/)

## Requirements

- Docker
- docker-compose
- netcat (for port checking)
- xclip (optional, for clipboard support)
- current user in docker group

## Data Management

### Persistent Data Location on Host

Bookmark data is stored in:
- `./bookmarks/<name>/` by default
- Configurable via `HOST_VOLUME_DIR` or full custom path (recommended)

### Deletion
The delete command removes:
1. Container instance
2. Environment configuration
3. All bookmark data

Requires two confirmations:
```bash
./bm delete mybookmarks
```
## Customization

### Title and Color Theme

If you just want to generate custom CSS for an existing linkding instance:

```bash
./bm css throwawayname 
```

otherwise use the bookmarks instance name and a file will be created at `containers/<name>.custom.<scheme>.css` that you can reuse without generating again.

```bash
./bm css <name> 
```

Running the css command will walk you through setting

1. custom webpage title
2. Webpage color theme.   

environment variables of these settings will be saved in the bookmarks env file and if the css command is issued again will be used as defaults.  

once the css generator is done it will put the content in the clipboard (using xclip) and also show the in the terminal for copy, or you can open your favorite edtior to review and copy.

Then you paste that css into the Custom CSS field in the setting page, general tab followed by save.  And bang! your new colors and title.

### Theme Generation

The theme generator creates a complete CSS variable-based theme from a single base color:

1. **Base Color Selection**: Choose any color in HEX format (#RRGGBB) to define your theme's primary color
2. **Color Scale Generation**: The script calculates a complete set of contrast levels (5%-90%) derived from your base color
3. **Adaptive Text Colors**: Text colors are generated with proper hierarchy and appropriate contrast for readability
4. **Light/Dark Mode**: The theme generator handles both light and dark modes by inverting color relationships
5. **UI Element Styling**: Generates appropriate colors for buttons, inputs, menus, and interactive states
6. **Logo Integration**: Automatically calculates logo hue rotation to match your chosen theme

The theme system uses CSS variables exclusively, allowing for:
- Complete theme transformation without touching HTML
- Proper color relationships throughout the UI
- Consistent contrast levels for accessibility
- Dynamic adjustments of all derived colors when just the base color changes

This generator is based on color theory principles to ensure all generated themes maintain proper contrast ratios and visual hierarchy regardless of the chosen base color.

The actual color calculations are performed in the `maketheme.py` script, which contains detailed documentation about the color theory implementation. For those interested in the technical details or adapting the theme generator for other projects, this file provides a comprehensive overview of the approach.

### Logo Replacement

A template SVG file is provided in `assets/circle-template.svg` to help create custom logos with the correct base color (#815EE8).

**Steps to create a custom logo:**

1. Start with the provided template: `assets/circle-template.svg`
2. Edit the SVG in your preferred vector editor (Inkscape, Illustrator, or online SVG editors)
   - **Alternative:** Use an AI assistant to generate SVG code from a simple description (e.g., "Create an SVG logo of a cat with the main color #815EE8 and transparent background")
3. Keep the purple color (#815EE8) as your main color for proper theme rotation
4. Save your modified SVG as `assets/custom-logo.svg`
5. Convert to PNG using ImageMagick:
   ```bash
   magick assets/custom-logo.svg -background none -resize 100x100 assets/custom-logo.png
   ```

**IMPORTANT:** The image MUST have:
- Transparent background (not white)
- Main logo color should match Linkding's purple base color (#815EE8)
- PNG format
- Square aspect ratio (1:1)
- ~100x100px recommended size

The theme generator automatically rotates the logo's hue based on your selected theme color. This rotation calculation assumes your logo starts with the default Linkding purple color. Using a different base color will result in incorrect color transformations when themes are applied.




