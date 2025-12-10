# Scanbox UI Redesign - Cybersecurity Theme

## Overview
Complete UI overhaul with a modern cybersecurity aesthetic featuring neon accents, dark backgrounds, and animated effects.

## Color Palette

### Primary Colors
- **Cyber Primary**: `#00ff88` (Neon Green) - Main accent color
- **Cyber Secondary**: `#00d9ff` (Cyan) - Secondary accent
- **Cyber Accent**: `#ff006e` (Hot Pink) - Warning/critical states

### Status Colors
- **Success**: `#00ff88` (Neon Green)
- **Warning**: `#ffaa00` (Amber)
- **Danger**: `#ff3366` (Red)
- **Critical**: `#ff006e` (Hot Pink)

### Background Colors
- **Primary BG**: `#0a0e27` (Deep Dark Blue)
- **Secondary BG**: `#0f1729` (Navy)
- **Card BG**: `#141b2d` (Dark Blue-Gray)
- **Elevated BG**: `#1a2332` (Lighter Blue-Gray)

### Text Colors
- **Primary Text**: `#e8f4f8` (Light Cyan)
- **Secondary Text**: `#a0c4d9` (Muted Cyan)
- **Muted Text**: `#6b8299` (Gray Blue)

## Key Design Features

### 1. **Animated Background**
- Grid pattern with subtle neon green lines
- Pulsing radial gradients
- Fixed position overlay with animated glow effect

### 2. **Sidebar Navigation**
- Glass-morphism effect with backdrop blur
- Animated scan line effect (vertical gradient)
- Hover states with neon glow
- Active tab highlighting with gradient background
- Logo floating animation

### 3. **Branding**
- **Name**: Scanbox (replacing MailShield Pro)
- **Logo**: 📦 (Box emoji)
- **Typography**: Monospace fonts (JetBrains Mono, Fira Code, Roboto Mono)
- **Logo Effect**: XML-style brackets `< Scanbox />`

### 4. **Buttons**
- Primary: Neon green gradient with ripple effect on hover
- Secondary: Cyan outline with shimmer animation
- Hover effects: Lift (translateY) + enhanced glow
- Letter spacing: 1.5px for uppercase text

### 5. **Input Fields**
- Dark background with subtle neon green tint
- Focused state: Green border with multi-layer glow
- Monospace font for technical feel

### 6. **Cards & Containers**
- Dark card backgrounds with subtle borders
- Shimmer animation on scan cards
- Hover effects with shadow and glow
- Left border accents for status (safe/warning/danger)

### 7. **Badges**
- Box shape (border-radius: 4px)
- Color-coded with matching glow effects
- Uppercase text with wide letter spacing
- Border matching badge color

### 8. **Email Cards**
- Left border indicates status
- Hover reveals inner glow effect
- Smooth elevation on hover

### 9. **Status Messages**
- Left accent bar with glow
- Color-coded backgrounds
- Slide-in animation
- Icon + text layout

### 10. **Stat Cards**
- Bottom accent line animation on hover
- Glowing numbers with text-shadow
- Lift effect on hover

### 11. **History Cards**
- Top border scan effect on hover
- Card elevation with neon glow
- Cybersecurity-themed transitions

### 12. **Risk Badges**
- Rotating conic gradient border effect
- Inner and outer glow
- Animated spinning gradient
- Large numbers with text shadow

## Animations

### Global Animations
- `fadeIn`: Smooth opacity fade (0.5s)
- `slideIn`: Left slide with opacity (0.3s)
- `spin`: Loading spinner rotation (0.6s)
- `pulseGlow`: Background pulsing (8s infinite)
- `scanLine`: Vertical scan line (3s infinite)
- `logoFloat`: Floating logo (3s infinite)
- `shimmer`: Horizontal shimmer effect (3s infinite)
- `rotateBadge`: Rotating badge gradient (4s infinite)

## Typography
- **Font Family**: JetBrains Mono, Fira Code, Roboto Mono (monospace)
- **Headings**: 800 weight, uppercase, wide letter spacing
- **Body**: 600-700 weight
- **Labels**: 600 weight, 13px, uppercase, 0.5px letter spacing
- **Buttons**: 700 weight, 14px, uppercase, 1.5px letter spacing

## Special Effects

### Glow Effects
- Box shadows with RGBA colors for soft glows
- Multiple layered shadows for depth
- Color-matched glows for status indicators

### Border Effects
- Gradient borders using pseudo-elements
- Animated scan lines
- Accent bars with glow

### Hover States
- Transform: translateY (lift effect)
- Enhanced shadows and glows
- Border color transitions
- Background opacity changes

## Responsive Breakpoints
- Mobile optimization maintained
- Sidebar: Fixed 280px width
- Main content: margin-left 280px
- Grid layouts use auto-fill with minmax

## Browser Compatibility
- Modern CSS features (CSS Grid, Flexbox, custom properties)
- Backdrop filter for glass effects
- Conic gradients for animations
- Text gradients with webkit support

## Performance Optimizations
- CSS transitions use cubic-bezier easing
- Animations use transform (GPU accelerated)
- Will-change hints where appropriate
- Reduced animation duration (0.3s-0.6s)

## Accessibility
- High contrast color scheme (dark bg, light text)
- Clear status indicators (color + text)
- Readable font sizes (13px-14px base)
- Focus states with visible outlines

---

**Theme**: Dark Cybersecurity | **Style**: Neon Futuristic | **Brand**: Scanbox
