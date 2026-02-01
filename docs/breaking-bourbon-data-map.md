# Breaking Bourbon Data Mapping Reference

**Purpose:** Document the structure and location of data fields in Breaking Bourbon reviews  
**Example Review:** https://www.breakingbourbon.com/review/heaven-hill-grain-to-glass-rye-2025  
**Last Updated:** October 27, 2025

---

## Data Fields to Capture

### 1. **Whiskey Name**
- **Example:** Heaven Hill Grain to Glass Rye 2025
- **Data Type:** String (text)
- **HTML Location:** [To be filled in Module 1.3]
- **CSS Selector:** [To be filled in Module 1.3]
- **Notes:** Usually in page title and main heading

---

### 2. **Classification**
- **Example:** Straight Rye Whiskey
- **Data Type:** String
- **HTML Location:** [To be filled in Module 1.3]
- **CSS Selector:** [To be filled in Module 1.3]
- **Notes:** Type of whiskey (Bourbon, Rye, etc.)

---

### 3. **Company**
- **Example:** Heaven Hill Distillery
- **Data Type:** String
- **HTML Location:** [To be filled in Module 1.3]
- **CSS Selector:** [To be filled in Module 1.3]
- **Notes:** Parent company or brand owner

---

### 4. **Distillery**
- **Example:** Heaven Hill Distillery
- **Data Type:** String
- **HTML Location:** [To be filled in Module 1.3]
- **CSS Selector:** [To be filled in Module 1.3]
- **Notes:** May be same as Company or different

---

### 5. **Release Date**
- **Example:** 2025
- **Data Type:** String (could be year only, or full date)
- **HTML Location:** [To be filled in Module 1.3]
- **CSS Selector:** [To be filled in Module 1.3]
- **Notes:** Format varies - sometimes just year, sometimes month/year
- **Edge Cases:** "N/A", "Limited Release 2024", etc.

---

### 6. **Proof**
- **Example:** 100
- **Data Type:** Number (float or int)
- **HTML Location:** [To be filled in Module 1.3]
- **CSS Selector:** [To be filled in Module 1.3]
- **Notes:** May include " proof" text that needs stripping
- **Edge Cases:** Range like "90-100", "Cask Strength", "N/A"

---

### 7. **Age**
- **Example:** 4 Years
- **Data Type:** String
- **HTML Location:** [To be filled in Module 1.3]
- **CSS Selector:** [To be filled in Module 1.3]
- **Notes:** May include "years", "months", or be "NAS" (No Age Statement)
- **Edge Cases:** "NAS", "4-6 Years", "N/A"

---

### 8. **Mashbill**
- **Example:** 51% Rye, 39% Corn, 10% Malted Barley
- **Data Type:** String
- **HTML Location:** [To be filled in Module 1.3]
- **CSS Selector:** [To be filled in Module 1.3]
- **Notes:** Grain recipe percentages
- **Edge Cases:** "Undisclosed", "Proprietary", ranges, missing

---

### 9. **Color**
- **Example:** Copper
- **Data Type:** String
- **HTML Location:** [To be filled in Module 1.3]
- **CSS Selector:** [To be filled in Module 1.3]
- **Notes:** Subjective description of appearance
- **Edge Cases:** May be missing on some reviews

---

### 10. **MSRP / Price**
- **Example:** $55
- **Data Type:** String (keep $ symbol) or Number
- **HTML Location:** [To be filled in Module 1.3]
- **CSS Selector:** [To be filled in Module 1.3]
- **Notes:** Suggested Retail Price
- **Edge Cases:** "$50-60", "~$55", "N/A", "Not Available"

---

### 11. **Nose (Tasting Notes)**
- **Example:** "Brown sugar, cinnamon, nutmeg, vanilla, and baking spices lead the way..."
- **Data Type:** String (long text)
- **HTML Location:** [To be filled in Module 1.3]
- **CSS Selector:** [To be filled in Module 1.3]
- **Notes:** Full paragraph of tasting notes for aroma
- **Edge Cases:** May be multiple paragraphs

---

### 12. **Taste / Palate (Tasting Notes)**
- **Example:** "Toasted grains and oak lead the way along with a nice helping of vanilla..."
- **Data Type:** String (long text)
- **HTML Location:** [To be filled in Module 1.3]
- **CSS Selector:** [To be filled in Module 1.3]
- **Notes:** Full paragraph of flavor tasting notes
- **Edge Cases:** May be multiple paragraphs

---

### 13. **Finish (Tasting Notes)**
- **Example:** "Medium long finish that features sweet cinnamon and nutmeg..."
- **Data Type:** String (long text)
- **HTML Location:** [To be filled in Module 1.3]
- **CSS Selector:** [To be filled in Module 1.3]
- **Notes:** Description of aftertaste and finish
- **Edge Cases:** May be multiple paragraphs

---

### 14. **Rating / Score**
- **Example:** Not visible on this review
- **Data Type:** Number or String
- **HTML Location:** [To be filled in Module 1.3]
- **CSS Selector:** [To be filled in Module 1.3]
- **Notes:** Need to check if Breaking Bourbon uses numeric scores
- **Edge Cases:** May not exist on all reviews

---

### 15. **Review URL**
- **Example:** https://www.breakingbourbon.com/review/heaven-hill-grain-to-glass-rye-2025
- **Data Type:** String (URL)
- **HTML Location:** N/A (this is the page we're scraping)
- **Notes:** Store the source URL for reference
- **Why Important:** Link back to original review, avoid duplicates

---

### 16. **Review Date / Publication Date**
- **Example:** Need to find on page
- **Data Type:** Date or String
- **HTML Location:** [To be filled in Module 1.3]
- **CSS Selector:** [To be filled in Module 1.3]
- **Notes:** When review was published - critical for finding new reviews
- **Edge Cases:** Format may vary (Oct 27, 2025 vs 10/27/2025)

---

### 17. **Date Scraped (Metadata)**
- **Example:** 2025-10-27 14:30:00
- **Data Type:** Datetime
- **HTML Location:** N/A (we generate this)
- **Notes:** Timestamp when we scraped the data
- **Why Important:** Track data freshness, debugging

---

## Common Patterns to Note

**Things that might be missing:**
- Some reviews may not have all fields filled
- Mashbill often "Undisclosed"
- Age might be "NAS" (No Age Statement)
- Color description sometimes omitted

**Text that needs cleaning:**
- Proof: "100 proof" → extract just "100"
- Price: "$55" or "$50-60" → need to handle ranges
- Age: "4 Years" → might want to extract just "4"

**Data validation considerations:**
- Proof should be reasonable (40-140 range)
- Price should be positive number
- URLs should be valid
- Dates should parse correctly

---

## Future Expansion Notes

**When adding more sites:**
- Create similar mapping docs for each site
- Note differences in structure
- Document site-specific quirks
- Keep field names consistent across sites

---

## Questions to Answer in Module 1.3

1. Where exactly in the HTML is each field?
2. What CSS selectors can target each field uniquely?
3. Are fields in consistent locations across different reviews?
4. What happens when a field is missing?
5. Is there a structured data format (JSON-LD, Schema.org)?