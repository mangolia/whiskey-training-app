# Whiskey Sensory Categorization Master Guide

**Version:** 1.0
**Date:** January 19, 2026
**Purpose:** Unified documentation for categorizing whiskey sensory data for database entry and training app use

---

## Table of Contents

1. [Overview & Philosophy](#overview--philosophy)
2. [Multi-Dimensional Categorization System](#multi-dimensional-categorization-system)
3. [Database Schema Recommendations](#database-schema-recommendations)
4. [Flavor Taxonomy (11 Primary Categories)](#flavor-taxonomy-11-primary-categories)
5. [Structural Attributes (Mouthfeel, Body, Texture)](#structural-attributes)
6. [Finish Attributes (Length, Development, Heat)](#finish-attributes)
7. [Quality Descriptors (Balance, Character)](#quality-descriptors)
8. [Complete Recategorization Mapping](#complete-recategorization-mapping)
9. [Hierarchical Structure Guide](#hierarchical-structure-guide)
10. [Categorization Decision Trees](#categorization-decision-trees)
11. [Edge Cases & Ambiguous Descriptors](#edge-cases--ambiguous-descriptors)
12. [Implementation Roadmap](#implementation-roadmap)

---

## Overview & Philosophy

### The Problem

The current single-dimension categorization system (9 categories) has resulted in:
- **30% of flavors** in "Other" category (188 out of 624)
- **Mixed descriptor types** - flavors, mouthfeel, finish characteristics all in one system
- **No hierarchical structure** - "Cherry" and "Dark Cherry" treated as separate, unrelated items
- **Phase confusion** - descriptors that only apply to finish (e.g., "Long") mixed with nose/palate flavors

### The Solution

A **multi-dimensional categorization system** that separates:

1. **FLAVOR DESCRIPTORS** - What you taste and smell (nose, palate, sometimes finish)
2. **STRUCTURAL ATTRIBUTES** - Physical sensations (mouthfeel, body, texture, coating)
3. **FINISH ATTRIBUTES** - Post-swallow characteristics (length, development, heat type, temperature)
4. **QUALITY DESCRIPTORS** - Subjective assessments (balance, complexity, character)

### Key Principles

✅ **Separation of Concerns:** Flavors ≠ Mouthfeel ≠ Finish Characteristics
✅ **Hierarchical Organization:** Parent categories → Child descriptors (2 levels)
✅ **Phase Specificity:** Track where descriptors typically appear (Nose/Palate/Finish)
✅ **Consistency:** Clear rules for edge cases and ambiguous descriptors
✅ **Training-Focused:** Structure supports sensory training and palate development

---

## Multi-Dimensional Categorization System

### Dimension 1: FLAVOR DESCRIPTORS
**What it is:** Actual taste and aroma compounds
**Where it appears:** Primarily Nose and Palate, some in Finish
**Example:** "Cherry", "Vanilla", "Cinnamon", "Oak"

**11 Primary Categories:**
1. Fruity
2. Floral
3. Grainy/Malty
4. Woody
5. Sweet/Confectionery
6. Spicy
7. Smoky/Peaty
8. Winey/Sherried (NEW - currently missing)
9. Earthy/Mineral (NEW - currently missing)
10. Savory/Nutty (MERGED - was "Savory" + nuts from "Other")
11. Creamy/Dairy (NEW - currently missing)

**Note:** "Bitter" category removed - chocolate/cocoa moved to "Sweet/Confectionery" subcategory

### Dimension 2: STRUCTURAL ATTRIBUTES
**What it is:** Physical sensations in the mouth
**Where it appears:** Primarily Palate
**Example:** "Silky Mouthfeel", "Full-Bodied", "Oily", "Chewy"

**Categories:**
- Mouthfeel Texture (Silky, Velvety, Oily, Buttery, Chewy)
- Body (Thin, Light, Medium, Full, Thick)
- Coating Quality (Coating, Non-coating)

### Dimension 3: FINISH ATTRIBUTES
**What it is:** Post-swallow characteristics
**Where it appears:** Finish only
**Example:** "Long", "Lingering Heat", "Dry", "Warming"

**Categories:**
- Length (Short, Medium, Long, Very Long)
- Heat Type (Gentle Heat, Warming Heat, Bold Heat, Prickly Heat)
- Temperature (Warming, Hot, Cooling)
- Texture (Dry, Slightly Dry, Tannic, Mouthwatering)
- Development (Lingering, Building, Undulating)

### Dimension 4: QUALITY DESCRIPTORS
**What it is:** Subjective quality assessments
**Where it appears:** Overall impression
**Example:** "Well Balanced", "Bold", "Complex", "Youthful"

**Categories:**
- Balance (Well Balanced, Nicely Balanced, Straightforward)
- Character (Bold, Gentle, Delicate, Robust, Youthful, Mellow)
- Appeal (Inviting, Pleasant, Approachable, Unique, Intriguing)

---

## Database Schema Recommendations

### Proposed Table Structure

```sql
-- PRIMARY TABLES

-- 1. FLAVOR CATEGORIES (Parent categories)
CREATE TABLE flavor_categories (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(50) NOT NULL,
    description TEXT,
    display_order INT,
    color_hex VARCHAR(7),  -- For UI visualization
    icon_name VARCHAR(50)   -- For UI icons
);

-- 2. FLAVOR DESCRIPTORS (Child descriptors)
CREATE TABLE flavor_descriptors (
    descriptor_id SERIAL PRIMARY KEY,
    category_id INT REFERENCES flavor_categories(category_id),
    parent_descriptor_id INT REFERENCES flavor_descriptors(descriptor_id),  -- For hierarchy
    descriptor_name VARCHAR(100) NOT NULL,
    descriptor_variants TEXT[],  -- Alternative spellings: ["Crème Brûlée", "Creme Brulee"]
    typical_phases VARCHAR(20)[],  -- ['Nose', 'Palate', 'Finish']
    intensity_range VARCHAR(20),  -- 'Low', 'Medium', 'High'
    common_in_styles VARCHAR(50)[],  -- ['Bourbon', 'Scotch', 'Rye']
    definition TEXT,  -- User-facing explanation
    training_notes TEXT  -- Tips for identifying this descriptor
);

-- 3. STRUCTURAL ATTRIBUTES
CREATE TABLE structural_attributes (
    attribute_id SERIAL PRIMARY KEY,
    attribute_type VARCHAR(20),  -- 'mouthfeel', 'body', 'coating'
    attribute_name VARCHAR(50) NOT NULL,
    description TEXT,
    intensity_scale_min INT DEFAULT 1,
    intensity_scale_max INT DEFAULT 10
);

-- 4. FINISH ATTRIBUTES
CREATE TABLE finish_attributes (
    attribute_id SERIAL PRIMARY KEY,
    attribute_type VARCHAR(20),  -- 'length', 'heat', 'temperature', 'texture', 'development'
    attribute_name VARCHAR(50) NOT NULL,
    description TEXT,
    numeric_equivalent INT  -- For "Short"=1, "Medium"=2, "Long"=3, etc.
);

-- 5. QUALITY DESCRIPTORS
CREATE TABLE quality_descriptors (
    descriptor_id SERIAL PRIMARY KEY,
    descriptor_type VARCHAR(20),  -- 'balance', 'character', 'appeal'
    descriptor_name VARCHAR(50) NOT NULL,
    description TEXT,
    valence VARCHAR(20)  -- 'positive', 'neutral', 'negative' for training feedback
);

-- RELATIONSHIP TABLES

-- 6. REVIEW SENSORY DATA (Links reviews to descriptors)
CREATE TABLE review_flavor_data (
    review_id INT,
    descriptor_id INT REFERENCES flavor_descriptors(descriptor_id),
    phase VARCHAR(20),  -- 'Nose', 'Palate', 'Finish'
    intensity INT CHECK (intensity BETWEEN 1 AND 10),
    notes TEXT,
    PRIMARY KEY (review_id, descriptor_id, phase)
);

CREATE TABLE review_structural_data (
    review_id INT,
    attribute_id INT REFERENCES structural_attributes(attribute_id),
    intensity INT CHECK (intensity BETWEEN 1 AND 10),
    notes TEXT,
    PRIMARY KEY (review_id, attribute_id)
);

CREATE TABLE review_finish_data (
    review_id INT,
    attribute_id INT REFERENCES finish_attributes(attribute_id),
    value VARCHAR(50),  -- Can be text like "Long" or numeric
    notes TEXT,
    PRIMARY KEY (review_id, attribute_id)
);

CREATE TABLE review_quality_data (
    review_id INT,
    descriptor_id INT REFERENCES quality_descriptors(descriptor_id),
    notes TEXT,
    PRIMARY KEY (review_id, descriptor_id)
);
```

### Why This Structure?

**Benefits:**
- ✅ Clean separation of different descriptor types
- ✅ Hierarchical flavor organization (parent_descriptor_id)
- ✅ Phase-specific tracking (typical_phases field)
- ✅ Variant handling (alternative spellings)
- ✅ Training-focused (training_notes, definitions)
- ✅ Flexible intensity scales per attribute type
- ✅ Easy to query and filter

**Query Examples:**
```sql
-- Get all child descriptors for "Fruity" category
SELECT fd.descriptor_name, fd.parent_descriptor_id
FROM flavor_descriptors fd
JOIN flavor_categories fc ON fd.category_id = fc.category_id
WHERE fc.category_name = 'Fruity'
ORDER BY fd.parent_descriptor_id, fd.descriptor_name;

-- Get all nose descriptors for a review
SELECT fc.category_name, fd.descriptor_name, rfd.intensity
FROM review_flavor_data rfd
JOIN flavor_descriptors fd ON rfd.descriptor_id = fd.descriptor_id
JOIN flavor_categories fc ON fd.category_id = fc.category_id
WHERE rfd.review_id = 123 AND rfd.phase = 'Nose'
ORDER BY rfd.intensity DESC;

-- Get finish characteristics
SELECT fa.attribute_type, fa.attribute_name, rfd.value
FROM review_finish_data rfd
JOIN finish_attributes fa ON rfd.attribute_id = fa.attribute_id
WHERE rfd.review_id = 123;
```

---

## Flavor Taxonomy (11 Primary Categories)

### 1. FRUITY
**Description:** All fruit-derived flavors including fresh, dried, cooked, and citrus
**Common in:** All whiskey styles
**Typical phases:** Nose (primary), Palate, Finish

**Subcategories:**
- **Citrus** (Parent)
  - Lemon, Lime, Orange, Orange Zest, Orange Peel, Orange Rind, Grapefruit, Bergamot, Lemon Zest, Citrus Zest
- **Orchard Fruits** (Parent)
  - Apple, Green Apple, Pear, Quince, Crisp Apple, Baked Apple, Stewed Apples, Dried Apple
- **Stone Fruits** (Parent)
  - Cherry, Peach, Apricot, Plum, Nectarine, Dark Cherry, Black Cherry, Dried Apricot
- **Berries** (Parent)
  - Raspberry, Strawberry, Blackberry, Cranberry, Blueberry, Black Raspberry, Dark Berries, Mixed Berries
- **Dried Fruits** (Parent)
  - Raisin, Fig, Date, Prune, Golden Raisin, Dried Cherry, Dried Fruit
- **Tropical Fruits** (Parent)
  - Banana, Pineapple, Mango, Papaya, Cantaloupe, Passion Fruit
- **Other Fruits** (Parent)
  - Grape, White Grape, Black Currant, Pomegranate, Summer Fruits

### 2. FLORAL
**Description:** Flower-derived aromas, perfumed notes
**Common in:** Scotch (especially Lowland/Speyside), Irish
**Typical phases:** Nose (primary)

**Subcategories:**
- **Fresh Flowers** (Parent)
  - Floral, Lavender, Hibiscus, Floral Notes
- **Honeyed Flowers** (Parent)
  - Honeysuckle

### 3. GRAINY/MALTY
**Description:** Cereal grains, malt character, bread notes
**Common in:** All styles, especially young/grain-forward expressions
**Typical phases:** Nose, Palate

**Subcategories:**
- **Raw Grain** (Parent)
  - Grain, Corn, Sweet Corn, Rye Grain, Wheat Grain, Raw Grain, Fresh Grain, Cereal Grain
- **Malted Grain** (Parent)
  - Malt, Malted Barley, Roasted Malt, Chocolate Malt, Toasted Malt, Malty
- **Bread/Baked** (Parent)
  - Fresh Baked Bread, Rye Bread, Cornbread, Toast, Dough, Bread Dough, Pretzel Dough
- **Breakfast Cereal** (Parent)
  - Frosted Flakes Cereal, Honey Smacks Cereal, Kettle Corn, Oats

### 4. WOODY
**Description:** Wood influence from barrel aging
**Common in:** All aged whiskeys
**Typical phases:** Palate (primary), Finish

**Subcategories:**
- **Oak** (Parent)
  - Oak, Charred Oak, Toasted Oak, Aged Oak, Seasoned Oak, Dry Oak, Sweet Oak, Fresh Oak
- **Oak Character** (Parent)
  - Barrel Char, Tannic Oak, Chewy Oak, New Oak, French Oak, Thick Oak
- **Resinous Wood** (Parent)
  - Pine, Cedar, Sandalwood, Pine Needles, Evergreen
- **Wood Descriptors** (Parent)
  - Sawdust, Tree Bark

### 5. SWEET/CONFECTIONERY
**Description:** Sugar-derived sweetness, candies, desserts, chocolate
**Common in:** Bourbon (especially), all styles
**Typical phases:** Nose, Palate, Finish

**Subcategories:**
- **Sugar** (Parent)
  - Brown Sugar, Dark Brown Sugar, Burnt Sugar, Molasses, Syrup, Maple Syrup, Corn Syrup, Raw Sugar, Cane Sugar
- **Caramel** (Parent)
  - Caramel, Burnt Caramel, Butterscotch, Toffee, Caramel Chews, Toasted Caramel, Rich Caramel
- **Vanilla** (Parent)
  - Vanilla, Vanilla Bean, Vanilla Cream, Vanilla Extract, Vanilla Powder, Sweet Vanilla, Creamy Vanilla
- **Honey** (Parent)
  - Honey, Honeycomb, Spiced Honey, Dark Honey
- **Chocolate/Cocoa** (Parent) [MOVED FROM BITTER]
  - Chocolate, Dark Chocolate, Milk Chocolate, Baking Chocolate, Cocoa, Cocoa Powder, White Chocolate, Mexican Chocolate
- **Candy/Confection** (Parent)
  - Candy Corn, Cotton Candy, Marshmallow, Nougat, Bubble Gum, Red Hots Candy, Saltwater Taffy
- **Baked Goods** (Parent)
  - Graham Cracker, Pie Crust, Creme Brulee, Yellow Cake, French Toast, Tiramisu, Fudge

### 6. SPICY
**Description:** Spice-derived flavors, peppery heat, baking spices
**Common in:** Rye whiskey (especially), high-proof expressions
**Typical phases:** Palate (primary), Finish

**Subcategories:**
- **Rye Spice** (Parent)
  - Rye Spice, Bold Rye Spice, Gentle Rye Spice, Lingering Rye Spice, Touch Of Rye Spice
- **Baking Spices** (Parent)
  - Baking Spices, Cinnamon, Nutmeg, Allspice, Clove, Ginger, Cinnamon Stick, Cinnamon Powder
- **Pepper** (Parent)
  - Black Pepper, White Pepper, White Peppercorn, Green Peppercorn, Black Peppercorn, Peppercorn
- **Herbal Spices** (Parent)
  - Anise, Star Anise, Fennel, Mint, Fresh Mint, Peppermint, Dill

### 7. SMOKY/PEATY
**Description:** Smoke character from peat or barrel char
**Common in:** Islay Scotch, some American craft
**Typical phases:** Nose, Palate, Finish (intensifies)

**Subcategories:**
- **Peat Smoke** (Parent)
  - Peat, Smoky
- **Wood Smoke** (Parent)
  - Smoke, Campfire Smoke, Campfire, Burnt Brown Butter

### 8. WINEY/SHERRIED ⭐ NEW CATEGORY
**Description:** Wine/sherry cask influence
**Common in:** Scotch (sherry cask), finished bourbons
**Typical phases:** Nose, Palate, Finish

**Subcategories:**
- **Sherry Character** (Parent)
  - [Currently no specific descriptors in dataset, but framework supports: Oloroso, PX, Fino]
- **Wine Notes** (Parent)
  - Brandy, Stout (beer), Tequila, Agave
- **Grape/Wine Fruit** (Parent)
  - [Overlaps with Fruity category - may stay there]

### 9. EARTHY/MINERAL ⭐ NEW CATEGORY
**Description:** Earth, mineral, vegetal notes
**Common in:** Scotch, aged expressions
**Typical phases:** Nose, Palate

**Subcategories:**
- **Earthy** (Parent)
  - Earthy, Earthy Undertone, Slightly Earthy, Earthiness, Mushroom
- **Vegetal** (Parent)
  - Hay, Grass, Straw, Fresh Cut Grass, Grassy, Herbal, Herbal Undertone, Vegetative
- **Mineral** (Parent)
  - Wet Stone, Mineral Note

### 10. SAVORY/NUTTY
**Description:** Savory flavors, nuts, tobacco, leather
**Common in:** Aged whiskeys, sherry cask
**Typical phases:** Palate, Finish

**Subcategories:**
- **Leather/Tobacco** (Parent)
  - Leather, Dry Leather, Aged Leather, Tobacco, Tobacco Leaf, Cigar Box, Cigar Wrapper, Pipe Tobacco
- **Nuts** (Parent)
  - Walnut, Hazelnut, Pecan, Almond, Chestnut, Mixed Nuts, Roasted Nuts, Toasted Nuts, Peanut, Marzipan
- **Coffee/Tea** (Parent)
  - Coffee, Coffee Bean, Roasted Coffee Bean, Roasted Coffee, Green Tea, Black Tea, Steeped Tea
- **Savory Other** (Parent)
  - Soy Sauce, Root Beer, Cola, Amaretto

### 11. CREAMY/DAIRY ⭐ NEW CATEGORY
**Description:** Cream, butter, milk-based flavors
**Common in:** Bourbon, Irish whiskey
**Typical phases:** Palate (primary)

**Subcategories:**
- **Butter** (Parent)
  - Butter, Brown Butter, Browned Butter, Buttery Oak
- **Cream** (Parent)
  - Cream, Sweet Cream, Whipped Cream, Strawberry Cream, Orange Cream, Cream Soda, Creamed Corn
- **Custard/Dairy** (Parent)
  - Custard, Vanilla Custard, Coconut

---

## Structural Attributes

### MOUTHFEEL TEXTURE

**Category:** Physical texture sensations
**Phase:** Palate only

**Attributes:**
- Silky Mouthfeel
- Velvety Mouthfeel
- Oily Mouthfeel
- Buttery Mouthfeel
- Chewy Mouthfeel
- Creamy Mouthfeel
- Nice Mouthfeel (general positive)
- Smooth (implied, rarely explicitly stated)

**Intensity Scale:** 1-10 (how pronounced)

### BODY

**Category:** Weight and fullness
**Phase:** Palate only

**Attributes:**
- Thin Mouthfeel / Thin
- Light
- Medium Body / Medium
- Full-Bodied / Full
- Thick Mouthfeel / Thick

**Intensity Scale:** Use numeric mapping:
- Thin = 2
- Light = 3-4
- Medium = 5-6
- Full = 7-8
- Thick = 9-10

### COATING

**Category:** Residual coating sensation
**Phase:** Palate/Finish

**Attributes:**
- Coating (positive)
- Non-coating / Clean

---

## Finish Attributes

### LENGTH

**Category:** How long flavors persist
**Phase:** Finish only

**Attributes:**
- Short
- Medium Length / Medium
- Long
- Long Lasting
- Very Long
- Endless (rare, exceptional)

**Numeric Mapping:**
- Short = 1 (under 15 seconds)
- Medium = 2 (15-45 seconds)
- Long = 3 (45-90 seconds)
- Very Long = 4 (90+ seconds)

### HEAT TYPE

**Category:** Type of alcoholic warmth
**Phase:** Finish only

**Attributes:**
- Gentle Heat
- Some Heat
- Warming Heat / Warming
- Bold Heat
- Lingering Heat
- Prickly Heat
- Building Heat
- Undulating Heat
- Lingering Dry Heat
- Ramp Up Of Heat
- Rush Of Spice (spice-derived heat)

### TEMPERATURE

**Category:** Temperature sensation
**Phase:** Finish only

**Attributes:**
- Hot
- Warming
- Cool / Cooling (rare, from mint/menthol)
- Neutral

### FINISH TEXTURE

**Category:** Drying/tannic sensations
**Phase:** Finish only

**Attributes:**
- Dry
- Slightly Dry
- Touch Dry
- Mildly Dry
- Incredibly Dry
- Tannic
- Slightly Tannic
- Dryness (general)

### FINISH DEVELOPMENT

**Category:** How finish evolves
**Phase:** Finish only

**Attributes:**
- Lingering
- Lingering Sweetness
- Lingering Spice
- Lingering Sweet-Spicy Mix
- Lingering Warmth
- Building (intensifies)
- Tapering (fades gradually)

---

## Quality Descriptors

### BALANCE

**Category:** Harmony of elements
**Phase:** Overall assessment

**Descriptors:**
- Well Balanced
- Nicely Balanced
- Straightforward
- Balanced (implied in "Well Balanced")

**Valence:** Positive

### CHARACTER

**Category:** Personality/style
**Phase:** Overall assessment

**Descriptors:**

**Intensity:**
- Bold
- Robust
- Potent
- Punchy
- Intense
- Full-Flavored
- Rich

**Gentleness:**
- Gentle
- Delicate
- Mellow
- Approachable
- Light

**Age/Development:**
- Youthful
- Young (not necessarily negative)
- Mature
- Musty (can be positive or negative)

**Valence:** Neutral (context-dependent)

### APPEAL

**Category:** Subjective enjoyment
**Phase:** Overall assessment

**Descriptors:**

**Positive:**
- Inviting
- Sweet & Inviting
- Pleasing
- Pleasant
- Delicious
- Excellent
- Fantastic
- Unique
- Intriguing
- Lively
- Bright & Lively

**Neutral/Observational:**
- Classic Bourbon Scents
- Classic Scents
- Bakery Scents
- Full (can mean full-flavored or overwhelming)

**Valence:** Positive (mostly)

---

## Complete Recategorization Mapping

### Changes from Original "OTHER" Category (188 → Redistributed)

| Original Descriptor | NEW Category | NEW Dimension | Parent (if applicable) |
|---------------------|--------------|---------------|------------------------|
| Graham Cracker | Sweet/Confectionery | Flavor | Baked Goods |
| Long | LENGTH | Finish Attribute | - |
| Short | LENGTH | Finish Attribute | - |
| Medium Length | LENGTH | Finish Attribute | - |
| Cigar Box | Savory/Nutty | Flavor | Leather/Tobacco |
| Pie Crust | Sweet/Confectionery | Flavor | Baked Goods |
| Ethanol | CHEMICAL/SOLVENT | Flavor (Fault) | - |
| Lingering Heat | HEAT TYPE | Finish Attribute | - |
| Anise | Spicy | Flavor | Herbal Spices |
| Nougat | Sweet/Confectionery | Flavor | Candy/Confection |
| Sweet | [REMOVE - too generic] | - | - |
| Toasted Marshmallow | Sweet/Confectionery | Flavor | Candy/Confection |
| Creme Brulee | Sweet/Confectionery | Flavor | Baked Goods |
| Dry | FINISH TEXTURE | Finish Attribute | - |
| Mint | Spicy | Flavor | Herbal Spices |
| Rich | CHARACTER | Quality Descriptor | - |
| Cola | Savory/Nutty | Flavor | Savory Other |
| Hay | Earthy/Mineral | Flavor | Vegetal |
| Marshmallow | Sweet/Confectionery | Flavor | Candy/Confection |
| Hazelnut | Savory/Nutty | Flavor | Nuts |
| Slightly Dry | FINISH TEXTURE | Finish Attribute | - |
| Brown Butter | Creamy/Dairy | Flavor | Butter |
| Bubble Gum | Sweet/Confectionery | Flavor | Candy/Confection |
| Thin Mouthfeel | BODY | Structural Attribute | - |
| Light | CHARACTER | Quality Descriptor | - |
| Lingering | DEVELOPMENT | Finish Attribute | - |
| Black Currant | Fruity | Flavor | Berries |
| Herbal | Earthy/Mineral | Flavor | Vegetal |
| Agave | Winey/Sherried | Flavor | Wine Notes |
| Overall | [REMOVE - not a descriptor] | - | - |
| Pecan | Savory/Nutty | Flavor | Nuts |
| Yellow Cake | Sweet/Confectionery | Flavor | Baked Goods |
| Amaretto | Savory/Nutty | Flavor | Savory Other |
| Seared Mint | Spicy | Flavor | Herbal Spices |
| Dark Berries | Fruity | Flavor | Berries |
| Marzipan | Savory/Nutty | Flavor | Nuts |
| Mixed Berries | Fruity | Flavor | Berries |
| Grass | Earthy/Mineral | Flavor | Vegetal |
| Heat | TEMPERATURE | Finish Attribute | - |
| Well Balanced | BALANCE | Quality Descriptor | - |
| Touch Dry | FINISH TEXTURE | Finish Attribute | - |
| Youthful | CHARACTER | Quality Descriptor | - |
| Dill | Spicy | Flavor | Herbal Spices |
| Lingering Sweetness | DEVELOPMENT | Finish Attribute | - |
| Silky Mouthfeel | TEXTURE | Structural Attribute | - |
| Thick Mouthfeel | BODY | Structural Attribute | - |
| Toast | Grainy/Malty | Flavor | Bread/Baked |
| Berries | Fruity | Flavor | Berries |
| Buttery Mouthfeel | TEXTURE | Structural Attribute | - |
| Nutty | Savory/Nutty | Flavor | Nuts |
| Some Heat | HEAT TYPE | Finish Attribute | - |
| Straightforward | BALANCE | Quality Descriptor | - |
| Straw | Earthy/Mineral | Flavor | Vegetal |
| Velvety Mouthfeel | TEXTURE | Structural Attribute | - |
| Fresh Mint | Spicy | Flavor | Herbal Spices |
| Full-Flavored | CHARACTER | Quality Descriptor | - |
| Herbal Undertone | Earthy/Mineral | Flavor | Vegetal |
| Nice Mouthfeel | TEXTURE | Structural Attribute | - |
| Nicely Balanced | BALANCE | Quality Descriptor | - |
| Butter | Creamy/Dairy | Flavor | Butter |
| Dark Cherries | Fruity | Flavor | Stone Fruits (Cherry) |
| Grassy | Earthy/Mineral | Flavor | Vegetal |
| Inviting | APPEAL | Quality Descriptor | - |
| Nutty Undertone | Savory/Nutty | Flavor | Nuts |
| Pecan Pie | Sweet/Confectionery | Flavor | Baked Goods |
| Potent | CHARACTER | Quality Descriptor | - |
| Savory | [REMOVE - too generic] | - | - |
| Tree Bark | Woody | Flavor | Wood Descriptors |
| Warming Heat | HEAT TYPE | Finish Attribute | - |
| Bold | CHARACTER | Quality Descriptor | - |
| Cantaloupe | Fruity | Flavor | Tropical Fruits |
| Chestnut | Savory/Nutty | Flavor | Nuts |
| Coconut | Creamy/Dairy | Flavor | Custard/Dairy |
| Delicious | APPEAL | Quality Descriptor | - |
| Intriguing | APPEAL | Quality Descriptor | - |
| Mint Leaf | Spicy | Flavor | Herbal Spices |
| Pleasing | APPEAL | Quality Descriptor | - |
| Summer Berries | Fruity | Flavor | Berries |
| Touch Of Ethanol | CHEMICAL/SOLVENT | Flavor (Fault) | - |
| Unique | APPEAL | Quality Descriptor | - |
| Baked Pie Crust | Sweet/Confectionery | Flavor | Baked Goods |
| Black Currants | Fruity | Flavor | Berries |
| Browned Butter | Creamy/Dairy | Flavor | Butter |
| Fennel | Spicy | Flavor | Herbal Spices |
| French Toast | Sweet/Confectionery | Flavor | Baked Goods |
| Hot | TEMPERATURE | Finish Attribute | - |
| Mellow | CHARACTER | Quality Descriptor | - |
| Tiramisu | Sweet/Confectionery | Flavor | Baked Goods |
| Toasted Coconut | Creamy/Dairy | Flavor | Custard/Dairy |
| Brandy | Winey/Sherried | Flavor | Wine Notes |
| Dryness | FINISH TEXTURE | Finish Attribute | - |
| Excellent | APPEAL | Quality Descriptor | - |
| Fudge | Sweet/Confectionery | Flavor | Baked Goods |
| Nectarine | Fruity | Flavor | Stone Fruits |
| Pleasant | APPEAL | Quality Descriptor | - |
| Root Beer | Savory/Nutty | Flavor | Savory Other |
| Slightly Tannic | FINISH TEXTURE | Finish Attribute | - |
| Vegetative | Earthy/Mineral | Flavor | Vegetal |

[Continue for remaining 88 "Other" items...]

### Summary of Redistribution

**Original "Other" (188 items) → NEW Distribution:**
- Finish Attributes: ~35 items (Length, Heat, Texture, Development)
- Structural Attributes: ~15 items (Mouthfeel, Body)
- Quality Descriptors: ~25 items (Balance, Character, Appeal)
- Sweet/Confectionery: ~40 items (Baked goods, candies)
- Savory/Nutty: ~20 items (Nuts, tobacco)
- Creamy/Dairy: ~10 items (Butter, cream)
- Earthy/Mineral: ~15 items (Vegetal, herbal)
- Spicy: ~10 items (Herbal spices, mint)
- Other categories: ~10 items
- Remove (too generic/redundant): ~8 items

---

## Hierarchical Structure Guide

### Two-Level Hierarchy

**LEVEL 1: Primary Category**
Example: Fruity

**LEVEL 2: Parent Descriptor**
Example: Stone Fruits

**LEVEL 2: Child Descriptors**
Example: Cherry, Dark Cherry, Black Cherry, Dried Cherry, Luxardo Cherry

### Hierarchy Rules

1. **All flavors must have a Primary Category** (Level 1)
2. **Parent Descriptors are optional** but recommended for common groupings
3. **Child Descriptors can stand alone** if no parent makes sense
4. **Maximum 2 levels below Primary Category**

### Example Hierarchies

```
FRUITY (Category)
├── Citrus (Parent)
│   ├── Lemon
│   ├── Orange
│   ├── Orange Zest
│   ├── Orange Peel
│   └── Orange Rind
├── Stone Fruits (Parent)
│   ├── Cherry (can also be parent)
│   │   ├── Dark Cherry
│   │   ├── Black Cherry
│   │   ├── Dried Cherry
│   │   └── Luxardo Cherry
│   ├── Peach
│   ├── Apricot
│   │   └── Dried Apricot
│   └── Plum
└── Berries (Parent)
    ├── Raspberry
    │   ├── Black Raspberry
    │   └── Dark Raspberry
    ├── Strawberry
    ├── Blackberry
    └── Mixed Berries
```

```
SWEET/CONFECTIONERY (Category)
├── Caramel (Parent)
│   ├── Burnt Caramel
│   ├── Toasted Caramel
│   ├── Dark Caramel
│   ├── Salted Caramel
│   └── Caramel Chews
├── Vanilla (Parent)
│   ├── Vanilla Bean
│   ├── Vanilla Cream
│   ├── Vanilla Extract
│   └── Vanilla Powder
└── Chocolate/Cocoa (Parent)
    ├── Dark Chocolate
    ├── Milk Chocolate
    ├── Baking Chocolate
    └── Cocoa Powder
```

### When to Create a Parent

**Create a Parent Descriptor when:**
✅ You have 3+ related child descriptors
✅ The parent term is commonly used (e.g., "Citrus", "Oak")
✅ It helps with filtering/search ("Show me all oak variations")

**Don't create a Parent when:**
❌ Only 1-2 children exist
❌ The parent is too abstract (e.g., "Good Flavors")
❌ Children are not truly related

---

## Categorization Decision Trees

### Decision Tree 1: Is This a Flavor Descriptor?

```
START: New descriptor to categorize

Q1: Does it describe WHAT you taste/smell?
    YES → It's a FLAVOR DESCRIPTOR → Go to Tree 2
    NO → Go to Q2

Q2: Does it describe HOW the whiskey FEELS in your mouth?
    YES → STRUCTURAL ATTRIBUTE
          ├─ Texture word (silky, oily)? → Mouthfeel Texture
          ├─ Weight word (thin, full)? → Body
          └─ Coating sensation? → Coating
    NO → Go to Q3

Q3: Does it describe characteristics AFTER swallowing?
    YES → FINISH ATTRIBUTE
          ├─ Time duration? → Length
          ├─ Heat/warmth type? → Heat Type
          ├─ Temperature? → Temperature
          ├─ Drying sensation? → Finish Texture
          └─ How it evolves? → Development
    NO → Go to Q4

Q4: Does it describe OVERALL quality or character?
    YES → QUALITY DESCRIPTOR
          ├─ About harmony? → Balance
          ├─ About personality? → Character
          └─ About enjoyment? → Appeal
    NO → REMOVE (too generic or not a sensory descriptor)
```

### Decision Tree 2: Which Flavor Category?

```
START: Confirmed Flavor Descriptor

Q1: Is it fruit-related?
    YES → FRUITY
    NO → Q2

Q2: Is it flower-related or perfumed?
    YES → FLORAL
    NO → Q3

Q3: Is it grain, malt, bread, or cereal-related?
    YES → GRAINY/MALTY
    NO → Q4

Q4: Is it wood or barrel-related?
    YES → WOODY
    NO → Q5

Q5: Is it sugar, caramel, vanilla, honey, chocolate, or candy-related?
    YES → SWEET/CONFECTIONERY
    NO → Q6

Q6: Is it spice, pepper, or herb-related (including mint)?
    YES → SPICY
    NO → Q7

Q7: Is it smoke or peat-related?
    YES → SMOKY/PEATY
    NO → Q8

Q8: Is it wine, sherry, or other alcohol-related?
    YES → WINEY/SHERRIED
    NO → Q9

Q9: Is it earthy, vegetal, mineral, or grass-related?
    YES → EARTHY/MINERAL
    NO → Q10

Q10: Is it leather, tobacco, nut, coffee, or tea-related?
    YES → SAVORY/NUTTY
    NO → Q11

Q11: Is it cream, butter, or dairy-related?
    YES → CREAMY/DAIRY
    NO → EDGE CASE (see Edge Cases section)
```

---

## Edge Cases & Ambiguous Descriptors

### Compound Descriptors

**Problem:** "Vanilla Cream", "Caramel Apple", "Spiced Honey" - which category?

**Solution:**
1. **Identify dominant flavor** (usually the noun)
   - "Vanilla Cream" → Dominant: Vanilla → SWEET/CONFECTIONERY
   - "Caramel Apple" → Dominant: Caramel → SWEET/CONFECTIONERY
   - "Spiced Honey" → Dominant: Honey → SWEET/CONFECTIONERY

2. **Consider phase appearance**
   - If primarily on nose → Use most aromatic component
   - If primarily on palate → Use most taste-forward component

3. **Allow multi-categorization** (database supports this)
   - "Spiced Honey" → SWEET/CONFECTIONERY (primary) + SPICY (secondary tag)

### Cross-Category Descriptors

**Examples:**
- **"Toasted"** - Grainy/Malty OR Woody depending on context
  - "Toasted Oak" → WOODY
  - "Toast" alone → GRAINY/MALTY

- **"Burnt"** - Woody OR Sweet/Confectionery
  - "Burnt Caramel" → SWEET/CONFECTIONERY
  - "Burnt Oak" → WOODY

**Solution:** Use the noun/object being modified, not the adjective

### Flavors That Could Fit Multiple Categories

| Descriptor | Could Be... | CHOOSE | Reasoning |
|------------|-------------|---------|-----------|
| Coconut | Creamy/Dairy OR Woody (oak) | CREAMY/DAIRY | Flavor is creamy; oak influence is separate |
| Butter | Creamy/Dairy OR Sweet | CREAMY/DAIRY | Dairy product, not sugar-sweet |
| Mint | Spicy OR Herbal OR Finish (cooling) | SPICY | Herbal spice category; cooling is a finish attribute |
| Coffee | Savory OR Bitter OR Sweet | SAVORY/NUTTY | Roasted/savory character dominates |
| Chocolate | Sweet OR Bitter | SWEET/CONFECTIONERY | Confection category includes cocoa |
| Toffee | Sweet OR Savory | SWEET/CONFECTIONERY | Sugar-based candy |
| Leather | Savory OR Woody | SAVORY/NUTTY | Not wood-derived |

### Generic Descriptors to Remove

**These are too vague for training purposes:**
- "Sweet" (use specific: caramel, honey, vanilla)
- "Savory" (use specific: leather, tobacco, nuts)
- "Fruity" (use specific fruit)
- "Spicy" (use specific spice)
- "Oak" alone is OK (it's specific enough)
- "Overall" (not a descriptor)
- "Proof Shines Through" (describes alcohol strength, not flavor)

### Chemical/Fault Descriptors

**These indicate flaws or youth:**
- Ethanol
- Touch Of Ethanol
- Solvent
- Acetone

**Treatment:**
- Create a special "CHEMICAL/SOLVENT" sub-category under Woody/Other
- Flag as potential training red flags (identifying faults)
- Keep in database for completeness

---

## Implementation Roadmap

### Phase 1: Database Migration (Week 1-2)

**Tasks:**
1. ✅ Create new database tables (flavor_categories, flavor_descriptors, structural_attributes, finish_attributes, quality_descriptors)
2. ✅ Populate flavor_categories with 11 primary categories
3. ✅ Migrate existing 624 descriptors to new structure
4. ✅ Establish parent-child relationships (hierarchy)
5. ✅ Add phase information (typical_phases field)
6. ✅ Test queries and relationships

**Deliverables:**
- SQL migration scripts
- Populated tables with all 624+ descriptors properly categorized
- Hierarchy validation

### Phase 2: API/Backend Updates (Week 2-3)

**Tasks:**
1. ✅ Update API endpoints to support multi-dimensional queries
2. ✅ Create endpoint: `/api/flavors/category/{category_id}`
3. ✅ Create endpoint: `/api/flavors/hierarchy/{descriptor_id}`
4. ✅ Create endpoint: `/api/finish-attributes`
5. ✅ Create endpoint: `/api/structural-attributes`
6. ✅ Update review submission to handle all four dimensions
7. ✅ Build search/filter functionality

**Deliverables:**
- Updated API documentation
- Test coverage for new endpoints

### Phase 3: UI/UX Updates (Week 3-4)

**Tasks:**
1. ✅ Design category-based flavor selector (11 categories)
2. ✅ Implement hierarchical drill-down (Category → Parent → Child)
3. ✅ Separate UI sections:
   - Nose flavors
   - Palate flavors
   - Mouthfeel (structural)
   - Finish characteristics
   - Overall quality
4. ✅ Add intensity sliders per descriptor
5. ✅ Visual flavor wheel or radar chart

**Deliverables:**
- Updated review input form
- Category-based navigation
- User testing feedback

### Phase 4: Training Module Enhancement (Week 4-6)

**Tasks:**
1. ✅ Build category-specific training quizzes
2. ✅ Create "Find the Outlier" exercises (spot miscategorized flavors)
3. ✅ Implement difficulty progression (start with categories, then specific descriptors)
4. ✅ Add definitions and reference images for each descriptor
5. ✅ Track user proficiency by category

**Deliverables:**
- Training module with 11 category tracks
- Progress tracking dashboard
- Achievement/badge system

### Phase 5: Data Validation & Quality Control (Week 6-7)

**Tasks:**
1. ✅ Review all 624 descriptors for accuracy
2. ✅ Validate parent-child relationships
3. ✅ Check for duplicates and variants
4. ✅ Add missing descriptors from whiskey reviews
5. ✅ User testing with whiskey enthusiasts

**Deliverables:**
- Clean, validated dataset
- Feedback-incorporated improvements

### Phase 6: Documentation & Launch (Week 7-8)

**Tasks:**
1. ✅ Create user-facing flavor guide
2. ✅ Write admin documentation for adding new descriptors
3. ✅ Build onboarding tutorial for app users
4. ✅ Launch beta with select users
5. ✅ Monitor usage and gather feedback

**Deliverables:**
- User guide (PDF/web page)
- Admin manual
- Beta launch

---

## Quick Reference: Categorization Checklist

When adding a new descriptor to the database, complete this checklist:

### ☐ STEP 1: Identify Dimension
- [ ] Is it a FLAVOR? (What you taste/smell)
- [ ] Is it a STRUCTURAL attribute? (How it feels)
- [ ] Is it a FINISH attribute? (Post-swallow)
- [ ] Is it a QUALITY descriptor? (Overall assessment)

### ☐ STEP 2: Assign Primary Category (if Flavor)
- [ ] Which of the 11 categories does it belong to?
- [ ] Check decision tree if unsure

### ☐ STEP 3: Establish Hierarchy
- [ ] Does it have a parent descriptor?
- [ ] Is it a parent with children?
- [ ] Or is it standalone?

### ☐ STEP 4: Add Metadata
- [ ] Typical phases (Nose/Palate/Finish)
- [ ] Common in which whiskey styles?
- [ ] Intensity range (Low/Medium/High)
- [ ] Definition (user-facing)
- [ ] Training notes

### ☐ STEP 5: Check for Duplicates
- [ ] Are there similar descriptors? (e.g., "Creme Brulee" vs "Crème Brûlée")
- [ ] Add as variant if duplicate
- [ ] Link if related but different

### ☐ STEP 6: Test Query
- [ ] Can you retrieve it via category?
- [ ] Does hierarchy display correctly?
- [ ] Is it searchable?

---

## Appendix A: Complete Flavor Vocabulary (624+ Descriptors)

[See separate CSV export for complete listing with all fields]

---

## Appendix B: Training Quiz Examples

### Example 1: Category Identification Quiz

**Question:** Which category does "Toasted Marshmallow" belong to?

A) Smoky/Peaty
B) Sweet/Confectionery ✓
C) Grainy/Malty
D) Creamy/Dairy

**Explanation:** While it's "toasted," marshmallow is a candy/confection, making it Sweet/Confectionery.

### Example 2: Hierarchy Quiz

**Question:** Which of these is the PARENT descriptor?

A) Dark Cherry
B) Stone Fruits ✓
C) Luxardo Cherry
D) Cherry Cobbler

**Explanation:** Stone Fruits is the parent category that includes cherries, peaches, apricots, etc.

### Example 3: Dimension Identification Quiz

**Question:** "Silky Mouthfeel" is best described as a:

A) Flavor descriptor
B) Structural attribute ✓
C) Finish attribute
D) Quality descriptor

**Explanation:** It describes how the whiskey FEELS (texture), not what it tastes like.

---

## Appendix C: SQL Query Examples

### Query 1: Get All Descriptors in a Category with Hierarchy

```sql
WITH RECURSIVE descriptor_tree AS (
  -- Base case: parent descriptors
  SELECT
    fd.descriptor_id,
    fd.descriptor_name,
    fd.parent_descriptor_id,
    fd.descriptor_name as path,
    0 as level
  FROM flavor_descriptors fd
  WHERE fd.category_id = 1  -- Fruity
    AND fd.parent_descriptor_id IS NULL

  UNION ALL

  -- Recursive case: child descriptors
  SELECT
    fd.descriptor_id,
    fd.descriptor_name,
    fd.parent_descriptor_id,
    dt.path || ' > ' || fd.descriptor_name,
    dt.level + 1
  FROM flavor_descriptors fd
  JOIN descriptor_tree dt ON fd.parent_descriptor_id = dt.descriptor_id
)
SELECT * FROM descriptor_tree
ORDER BY path;
```

### Query 2: Get Complete Review Profile

```sql
-- Flavors by phase
SELECT
  'Flavor' as dimension,
  fc.category_name,
  fd.descriptor_name,
  rfd.phase,
  rfd.intensity
FROM review_flavor_data rfd
JOIN flavor_descriptors fd ON rfd.descriptor_id = fd.descriptor_id
JOIN flavor_categories fc ON fd.category_id = fc.category_id
WHERE rfd.review_id = 123

UNION ALL

-- Structural attributes
SELECT
  'Structural' as dimension,
  sa.attribute_type as category_name,
  sa.attribute_name as descriptor_name,
  'Palate' as phase,
  rsd.intensity
FROM review_structural_data rsd
JOIN structural_attributes sa ON rsd.attribute_id = sa.attribute_id
WHERE rsd.review_id = 123

UNION ALL

-- Finish attributes
SELECT
  'Finish' as dimension,
  fa.attribute_type as category_name,
  fa.attribute_name as descriptor_name,
  'Finish' as phase,
  NULL as intensity
FROM review_finish_data rfd
JOIN finish_attributes fa ON rfd.attribute_id = fa.attribute_id
WHERE rfd.review_id = 123

ORDER BY dimension, phase, category_name;
```

---

## Document Control

**Version History:**
- v1.0 (2026-01-19): Initial comprehensive guide

**Maintained By:** Whiskey Sensory Training App Team
**Next Review:** 2026-04-19 (Quarterly)

**Feedback:** Contact [email] with suggestions for new descriptors or categorization improvements.

---

*This guide is a living document and will be updated as new descriptors emerge and user feedback is incorporated.*
