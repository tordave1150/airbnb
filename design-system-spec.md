# Airbnb Analytics — Design System Specification v1.0

> **Brand-Grade Design System for Airbnb Data Intelligence**
> Follows the [nexu-io/open-design](https://github.com/nexu-io/open-design) philosophy:
> curated visual direction, anti-AI-slop quality, deterministic palette library.

---

## 1. Brand Identity

| Property         | Value                                            |
|------------------|--------------------------------------------------|
| **Name**         | Airbnb Analytics                                 |
| **Tagline**      | Travel marketplace intelligence                 |
| **Visual Metaphor** | Premium Editorial Magazine                     |
| **Personality**  | Warm, Authoritative, Pristine, Human             |
| **Logo Mark**    | 󱊖 Airbnb Bélo (Rausch)                          |
| **Favicon**      | Rausch circle on white background               |

### Design Direction: "Pristine Canvas"

A premium light-mode aesthetic that prioritizes content and photography.
Inspired by high-end travel journalism and minimalist editorial layouts.
Every pixel communicates transparency, warmth, and reliable data.

---

## 2. Color System

### 2.1 Core Palette

```
┌─────────────────────────────────────────────────┐
│  BACKGROUNDS & SURFACES                         │
├─────────────────────────────────────────────────┤
│  Canvas White  #FFFFFF   rgb(255,255,255)  BASE │
│  Soft Cloud    #F7F7F7   rgb(247,247,247)  SUB  │
│  Hairline      #DDDDDD   rgb(221,221,221)  BORD │
├─────────────────────────────────────────────────┤
│  ACCENT COLORS                                  │
├─────────────────────────────────────────────────┤
│  Rausch        #FF385C   rgb(255,56,92)    PRIMARY│
│  Deep Rausch   #E00B41   rgb(224,11,65)           │
│  Plus Magenta  #92174D   rgb(146,23,77)           │
│  Luxe Purple   #460479   rgb(70,4,121)            │
│  Info Blue     #428BFF   rgb(66,139,255)          │
├─────────────────────────────────────────────────┤
│  TEXT                                           │
├─────────────────────────────────────────────────┤
│  Ink Black     #222222   rgb(34,34,34)     PRIM │
│  Charcoal      #3F3F3F   rgb(63,63,63)          │
│  Ash Gray      #6A6A6A   rgb(106,106,106)  SEC  │
│  Mute Gray     #929292   rgb(146,146,146)       │
├─────────────────────────────────────────────────┤
│  SEMANTIC                                       │
├─────────────────────────────────────────────────┤
│  Success       #00A699   rgb(0,166,153)           │
│  Error         #C13515   rgb(193,53,21)           │
└─────────────────────────────────────────────────┘
```

### 2.2 Component Visuals

| Token                  | Value                          | Use                     |
|------------------------|--------------------------------|-------------------------|
| `--card-radius`        | `14px`                         | Listing cards, Charts   |
| `--button-radius`      | `8px`                          | CTAs, Inputs            |
| `--border-default`     | `1px solid #DDDDDD`            | Dividers, Grid lines    |
| `--shadow-layer-1`     | `rgba(0,0,0,0.02) 0 0 0 1px`   | Base card depth         |
| `--shadow-layer-2`     | `rgba(0,0,0,0.04) 0 2px 6px 0` | Mid card depth          |
| `--shadow-layer-3`     | `rgba(0,0,0,0.1) 0 4px 8px 0`  | Top card depth          |

---

## 3. Typography

### 3.1 Font Stack

| Role       | Family                          | Weights         | Fallback                |
|------------|---------------------------------|-----------------|-------------------------|
| **Primary**| Airbnb Cereal VF                | 500, 600, 700   | Circular, Inter, sans-serif |
| **Monospace**| SFMono-Regular                | 400, 600        | Menlo, Consolas, monospace |

### 3.2 Type Hierarchy

| Level      | Size (px) | Weight | Tracking | Case     |
|------------|-----------|--------|----------|----------|
| Hero Title | 48px      | 700    | -0.02em  | Sentence |
| Section Head| 28px     | 700    | -0.02em  | Sentence |
| Card Title | 21px      | 700    | 0        | Sentence |
| Body       | 16px      | 500    | 0        | Sentence |
| Label      | 14px      | 500    | 0        | Sentence |
| Metadata   | 12px      | 400    | 0        | Sentence |

---

## 4. Components

### 4.1 Buttons
- **Primary:** Rausch (#FF385C) background, White text.
- **Secondary:** White background, Ink Black text, Hairline border.
- **Hover:** Slight scale transform (0.96) or color deepening (Deep Rausch).

### 4.2 Cards
- Background: #FFFFFF
- Radius: 14px
- Border: 1px solid #DDDDDD
- Shadow: Stacked 3-layer elevation (Layer 1, 2, 3 combined).

---

## 5. Execution Guidelines

1. **Whitespace is Luxury:** Don't crowd the data. Use generous margins between sections.
2. **Photography First:** Use full-bleed, high-quality images where possible.
3. **500 is the Base:** Avoid thin (400) weights for primary reading; 500 provides authority.
4. **Rausch Sparingly:** Use the signature pink only for the most important actions or indicators.
