#!/usr/bin/env python3
"""
maketheme.py - Dynamic CSS Theme Generator for Linkding Bookmarks

This script generates a complete CSS color theme based on a single base color.
It's specifically designed to work with Linkding bookmarks manager's custom CSS
feature, allowing users to completely transform the UI with minimal effort.

This generator can potentially be used with any site using Tailwind CSS or similar
frameworks that support CSS variable-based theming, enabling runtime theme changes
without needing to rebuild CSS files.

Usage:
    python3 maketheme.py <hex_color> [light|dark]
    
    - hex_color: Base color in #RRGGBB format (e.g., #50B464)
    - scheme: Optional, 'light' or 'dark' (default is 'dark')

How it works:
    1. The script takes a base color and scheme (light/dark) as input
    2. It creates a neutral version of the color to establish a baseline
    3. It generates a complete set of CSS variables for:
       - Contrast levels (from 5% to 90%)
       - Text colors with proper hierarchical contrast
       - UI element colors (buttons, inputs, borders)
       - Interactive state colors (hover, focus, active)
    4. It calculates a hue rotation for the logo to match the selected theme
    5. Outputs a complete CSS theme that can be copied to Linkding's custom CSS field

Key Functions:
    - generate_theme(): The main function that produces the CSS output
    - hex_to_rgb(), rgb_to_hsl(): Color format conversion utilities
    - adjust_dl(): Creates a color between black and white using a neutral color's hue
      on a custom 0-2 scale with 1 being neutral
    - get_hue_rotation(): Calculates the hue rotation to transform logo colors

This script is part of the Linkding Bookmarks project and is intended to be
used through the associated shell script that provides a user-friendly interface.

Requirements:
    - Python 3.6 or higher
    - No external dependencies (uses only standard library)
"""

import sys
import colorsys
import re
from typing import Tuple, Dict

def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color to RGB."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hsl(r: int, g: int, b: int) -> Tuple[float, float, float]:
    """Convert RGB values to HSL."""
    # Convert RGB to range [0, 1]
    r, g, b = r/255.0, g/255.0, b/255.0
    # Use colorsys to convert to HSL
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return (h, s, l)

def rgb_to_str(rgb: Tuple[int, int, int]) -> str:
    """Convert RGB tuple to CSS rgb() string."""
    return f"rgb({rgb[0]}, {rgb[1]}, {rgb[2]})"

def rgba_to_str(rgb: Tuple[int, int, int], alpha: float) -> str:
    """Convert RGB tuple and alpha to CSS rgba() string."""
    return f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, {alpha})"

def adjust_rgb(rgb: Tuple[int, int, int], factor: float) -> Tuple[int, int, int]:
    """Adjust RGB values by factor."""
    return tuple(min(255, max(0, int(x * factor))) for x in rgb)

def get_neutral_rgb(rgb: Tuple[int, int, int]) -> Tuple[int, int, int]:
    """Convert RGB to a neutral mid-range version."""
    # Convert to HSL to analyze brightness
    h, s, l = rgb_to_hsl(*rgb)
    
    # Adjust lightness to mid-range (0.5)
    # This creates a "neutral" version of the color
    # that's neither too light nor too dark
    neutral_factor = 0.5 / l if l > 0 else 1.0
    
    return adjust_rgb(rgb, neutral_factor)

def scheme_adjust_rgb(rgb: Tuple[int, int, int], scheme: str, percent: float) -> Tuple[int, int, int]:
    """Adjust RGB values based on scheme and percentage."""
    # Convert percentage to factor (e.g., 20% -> 1.2 or 0.8)
    if scheme == 'dark':
        # Dark theme: positive % brightens, negative % darkens
        factor = 1 + (percent / 100)
    else:
        # Light theme: positive % darkens, negative % brightens
        factor = 1 - (percent / 100)
    
    return adjust_rgb(rgb, factor)

def get_hue_rotation(from_color: str, to_color: str) -> int:
    """Calculate hue rotation needed to go from one color to another."""
    from_rgb = hex_to_rgb(from_color)
    to_rgb = hex_to_rgb(to_color)
    
    # Convert both colors to HSL to get hues
    from_h = rgb_to_hsl(*from_rgb)[0] * 360
    to_h = rgb_to_hsl(*to_rgb)[0] * 360
    
    # Calculate shortest rotation
    rotation = to_h - from_h
    if abs(rotation) > 180:
        rotation = rotation - 360 if rotation > 0 else rotation + 360
        
    return int(rotation)

def adjust_dl(neutral_rgb: Tuple[int, int, int], position: float) -> Tuple[int, int, int]:
    """
    Create a color between black and white using a neutral color's hue.
    
    Args:
        neutral_rgb: Pre-calculated neutral RGB tuple
        position: Scale position from 0.0 (black) to 2.0 (white), with 1.0 being neutral
    
    Returns:
        RGB tuple for the resulting color
    """
    # Ensure position is within range
    position = max(0.0, min(2.0, position))
    
    if position < 1.0:
        # Black to neutral: Scale from 0-1 to 0-1
        factor = position
        return tuple(int(c * factor) for c in neutral_rgb)
    else:
        # Neutral to white: Scale from 1-2 to 0-1
        factor = position - 1.0
        return tuple(int(c + (255 - c) * factor) for c in neutral_rgb)

def scheme_adjust_dl(neutral_rgb: Tuple[int, int, int], scheme: str, position: float) -> Tuple[int, int, int]:
    """
    Adjust color position based on scheme using 0-2 scale.
    
    Args:
        neutral_rgb: Pre-calculated neutral RGB tuple
        scheme: 'dark' or 'light'
        position: How far to move from neutral (1.0):
                 0.0 = black
                 1.0 = neutral
                 2.0 = white
                 In dark theme: >1 brightens, <1 darkens
                 In light theme: <1 brightens, >1 darkens
    """
    if scheme == 'light':
        # Invert position around neutral point for light theme
        position = 2.0 - position
    
    return adjust_dl(neutral_rgb, position)

def get_position(color: Tuple[int, int, int], neutral_rgb: Tuple[int, int, int]) -> float:
    """Get current position of a color on 0-2 scale relative to neutral."""
    # Get brightness of both colors (use L from HSL)
    _, _, color_l = rgb_to_hsl(*color)
    _, _, neutral_l = rgb_to_hsl(*neutral_rgb)
    
    # If darker than neutral, scale 0-1
    if color_l <= neutral_l:
        return color_l / neutral_l
    # If lighter than neutral, scale 1-2
    else:
        return 1.0 + ((color_l - neutral_l) / (1.0 - neutral_l))

def rl_adjust(color: Tuple[int, int, int], shift: float, neutral_rgb: Tuple[int, int, int], scheme: str) -> Tuple[int, int, int]:
    """Adjust color relative to its current position."""
    current_pos = get_position(color, neutral_rgb)
    # Limit shift based on available range
    max_up = 2.0 - current_pos
    max_down = current_pos
    shift = max(-max_down, min(max_up, shift if scheme == 'dark' else -shift))
    return adjust_dl(neutral_rgb, current_pos + shift)

def rotate_hue(hex_color: str, degrees: int) -> str:
    """Rotate hue of a hex color by a given number of degrees."""
    rgb = hex_to_rgb(hex_color)
    h, s, l = rgb_to_hsl(*rgb)
    h = (h * 360 + degrees) % 360 / 360
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"

def generate_theme(base_color: str, scheme: str = 'dark') -> str:
    """Generate theme CSS based on base color."""
    # Convert base color to RGB and get neutral version once
    raw_rgb = hex_to_rgb(base_color)
    neutral_rgb = get_neutral_rgb(raw_rgb)
    
    # Create bound adjusters using pre-calculated neutral
    def adjust(position: float) -> Tuple[int, int, int]:
        return scheme_adjust_dl(neutral_rgb, scheme, position)
    
    def rel_adjust(color: Tuple[int, int, int], shift: float) -> Tuple[int, int, int]:
        return rl_adjust(color, shift, neutral_rgb, scheme)
    
    # Generate theme colors
    primary = adjust(0.3)    # Dark in dark theme, Light in light theme
    contrast = adjust(1.8)   # Light in dark theme, Dark in light theme
    
    # Calculate logo rotation
    logo_rotation = get_hue_rotation("#815EE8", base_color)
    
    css = f"""/* Generated theme from {base_color} */
:root {{

    /* Contrast levels */
    --contrast-5: {rgb_to_str(adjust(0.1))};     /* 5% contrast */
    --contrast-10: {rgb_to_str(adjust(0.2))};    /* 10% contrast */
    --contrast-20: {rgb_to_str(adjust(0.4))};    /* 20% contrast */
    --contrast-30: {rgb_to_str(adjust(0.6))};    /* 30% contrast */
    --contrast-40: {rgb_to_str(adjust(0.8))};    /* 40% contrast */
    --contrast-50: {rgb_to_str(adjust(1.0))};    /* 50% contrast (neutral) */
    --contrast-60: {rgb_to_str(adjust(1.2))};    /* 60% contrast */
    --contrast-70: {rgb_to_str(adjust(1.4))};    /* 70% contrast */
    --contrast-80: {rgb_to_str(adjust(1.6))};    /* 80% contrast */
    --contrast-90: {rgb_to_str(adjust(1.8))};    /* 90% contrast */

    /* Primary colors */
    --primary-color: {rgb_to_str(primary)};
    --primary-color-highlight: {rgb_to_str(rel_adjust(primary, 0.1))};
    --primary-color-shade: {rgb_to_str(rel_adjust(primary, -0.1))};
    --primary-overlay: {rgba_to_str(primary, 0.15)};

    /* Base theme colors */
    --body-color: {rgb_to_str(primary)};
    --body-color-contrast: var(--contrast-30);

    /* Text colors */
    --text-color: {rgb_to_str(contrast)};
    --secondary-text-color: {rgb_to_str(rel_adjust(contrast, -0.2))};
    --tertiary-text-color: {rgb_to_str(rel_adjust(contrast, -0.4))};
    --contrast-text-color: {rgb_to_str(adjust(2.0))};    /* White in dark theme, Black in light theme */
    --primary-text-color: {rgb_to_str(adjust(1.0))};   

    /* Link colors */
    --link-color: {rgb_to_str(adjust(1))}; /* works for either */
    --secondary-link-color: {rgb_to_str(adjust(1.2))};

    --alternative-color: {rgb_to_str(adjust(1))};
    --alternative-color-dark: {rgb_to_str(contrast)};

    /* Icon colors */
    --icon-color: var(--text-color);  

    /* Border colors */
    --border-color: var(--contrast-30);
    --secondary-border-color: var(--contrast-20);
    --focus-outline: 3px solid var(--contrast-40);

    /* Input styling */
    --input-bg: {rgb_to_str(rel_adjust(primary, 0.3))};
    --input-border: {rgb_to_str(rel_adjust(primary, 0.5))};
    --input-text: {rgb_to_str(rel_adjust(contrast, 0.1))};
    --input-bg-color: var(--input-bg);
    --input-disabled-bg-color: var(--contrast-30);          /* Use contrast scale for disabled state */
    --input-text-color: var(--input-text);
    --input-hint-color: var(--secondary-text-color);        /* Reuse secondary text color */
    --input-border-color: var(--border-color);             /* Reuse global border color */
    --input-placeholder-color: {rgba_to_str(contrast, 0.5)}; /* Semi-transparent version of text color */

    /* Form elements */
    --checkbox-bg-color: var(--contrast-10);
    --checkbox-checked-bg-color: var(--input-bg);
    --checkbox-disabled-bg-color: var(--primary);
    --checkbox-border-color: var(--border-color);
    --checkbox-icon-color: var(--contrast-text-color);

    /* Button styling */
    --btn-bg-color: {rgba_to_str(contrast, 0.5)};              /* Subtle background */
    --btn-hover-bg-color: {rgba_to_str(contrast, 0.6)};      /* Slightly more visible on hover */
    --btn-border-color: var(--border-color);        /* Match global borders */
    --btn-text-color: var(--input-text);           /* Match main text */
    --btn-icon-color: var(--btn-text-color);           /* Match icons */

    /* Special buttons - using predefined semantic colors */
    --btn-primary-bg-color: var(--btn-bg-color);
    --btn-primary-hover-bg-color: var(--btn-hover-bg-color);
    --btn-primary-text-color: var(--input-text);

    --btn-success-bg-color: var(--success-color);
    --btn-success-hover-bg-color: var(--success-color-highlight);
    --btn-success-text-color: var(--contrast-text-color);

    --btn-error-bg-color: var(--error-color);
    --btn-error-hover-bg-color: var(--error-color-highlight);
    --btn-error-text-color: var(--contrast-text-color);

    --btn-link-text-color: var(--link-color);
    --btn-link-hover-text-color: var(--link-color);

    /* Menu styling */
    --menu-bg-color: {rgb_to_str(rel_adjust(primary, 0.2))};     /* Slightly lighter/darker than body */
    --menu-border-color: var(--contrast-30);                      /* Consistent borders */
    --menu-item-color: var(--text-color);                        /* Normal text color */
    --menu-item-hover-color: var(--text-color);                  /* Keep text color on hover */
    --menu-item-bg-color: transparent;                           /* No background by default */
    --menu-item-hover-bg-color: var(--contrast-20);             /* Subtle hover effect */

    /* Tab styling - looks good, using text colors consistently */
    --tab-color: var(--text-color);
    --tab-hover-color: var(--primary-text-color);
    --tab-active-color: var(--primary-text-color);
    --tab-highlight-color: var(--primary-text-color);

    /* Bookmark styling - good hierarchy of text colors */
    --bookmark-title-color: var(--primary-text-color);
    --bookmark-description-color: var(--text-color);
    --bookmark-actions-color: var(--secondary-text-color);
    --bookmark-actions-hover-color: var(--text-color);

    /* Switch specific - good use of contrast scale */
    --switch-bg-color: var(--contrast-10);
    --switch-border-color: var(--border-color);
    --switch-toggle-color: var(--text-color);

    /* Modal additions */
    --modal-overlay-bg-color: {rgba_to_str(adjust(0.1), 0.5)};   /* Semi-transparent dark overlay */
    --modal-container-bg-color: {rgb_to_str(primary)};           /* Same as body background */
    --modal-container-border-color: var(--contrast-30);
    --modal-box-shadow: none;

    /* Bulk actions - good subtle background */
    --bulk-actions-bg-color: var(--contrast-5);

    color-scheme: {scheme};
}}

/* Special logo styling that can't be handled by variables */
.logo {{
    filter: hue-rotate({logo_rotation}deg) saturate(130%) brightness(120%) !important;
}}

}}"""
    return css

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: maketheme.py <hex_color> [light|dark]")
        sys.exit(1)
    
    color = sys.argv[1]
    scheme = sys.argv[2] if len(sys.argv) > 2 else 'dark'
    
    if not re.match(r'^#[0-9A-Fa-f]{6}$', color):
        print("Error: Color must be in hex format (e.g., #50B464)")
        sys.exit(1)
    
    print(generate_theme(color, scheme))