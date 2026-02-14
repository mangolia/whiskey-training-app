import React from 'react';
import { Card } from './Card';

export function DevSpecsScreen() {
  return (
    <div className="space-y-8 pt-6 pb-12">
      {/* Header */}
      <div className="text-center">
        <h1 className="mb-3">Development Specifications</h1>
        <p className="text-sm text-text-secondary max-w-md mx-auto">
          Complete design system, UX behavior, and implementation guidelines for the Whiskey Tasting Quiz application
        </p>
      </div>

      {/* Design Philosophy */}
      <Section title="Design Philosophy">
        <SpecCard>
          <h4 className="mb-3">Brand Identity</h4>
          <ul className="space-y-2 text-sm">
            <li><strong>Theme:</strong> Luxurious navy and gold inspired by high-end spirits branding</li>
            <li><strong>Atmosphere:</strong> Sophisticated moody aesthetic similar to Whisky Advocate meets modern web design</li>
            <li><strong>Target Audience:</strong> Whiskey enthusiasts testing their palate through professional reviews</li>
            <li><strong>Mobile-First:</strong> Optimized for 375px-480px screens with proper touch targets</li>
            <li><strong>Premium Feel:</strong> Subtle textures, shadows, and smooth animations throughout</li>
          </ul>
        </SpecCard>
      </Section>

      {/* Color System */}
      <Section title="Color System">
        <SpecCard>
          <h4 className="mb-3">Primary Colors</h4>
          <div className="space-y-3">
            <ColorSwatch color="#2a3c93" name="Primary Navy" usage="Main brand color, active states, primary buttons" />
            <ColorSwatch color="#d4af37" name="Accent Gold" usage="Highlights, active selections, premium badges" />
            <ColorSwatch color="#1e2d6e" name="Dark Navy" usage="Gradients, depth, secondary brand elements" />
          </div>
        </SpecCard>

        <SpecCard>
          <h4 className="mb-3">Neutral Colors</h4>
          <div className="space-y-3">
            <ColorSwatch color="#f5f1e8" name="Background Cream" usage="Main background, suggests aged paper texture" />
            <ColorSwatch color="#ffffff" name="Card White" usage="Card backgrounds, elevated surfaces" />
            <ColorSwatch color="#2d2d2d" name="Neutral Dark" usage="Primary text, headings" />
            <ColorSwatch color="#666666" name="Text Secondary" usage="Secondary text, metadata" />
            <ColorSwatch color="#e0d5c7" name="Neutral Light" usage="Borders, dividers, inactive states" />
          </div>
        </SpecCard>

        <SpecCard>
          <h4 className="mb-3">Semantic Colors</h4>
          <div className="space-y-3">
            <ColorSwatch color="#2e7d32" name="Success Green" usage="Correct answers, positive feedback" />
            <ColorSwatch color="#c62828" name="Error Red" usage="Incorrect answers, negative feedback" />
            <ColorSwatch color="#f57c00" name="Warning Orange" usage="Alerts, important notices" />
          </div>
        </SpecCard>
      </Section>

      {/* Typography */}
      <Section title="Typography">
        <SpecCard>
          <h4 className="mb-3">Font Families</h4>
          <ul className="space-y-3 text-sm">
            <li>
              <strong>Headings:</strong> Playfair Display (serif)
              <div className="mt-1 text-text-secondary">Usage: All h1, h2, h3, h4 elements, section titles, whiskey names</div>
              <div className="mt-1 text-text-secondary">Weight: 600 (semi-bold) for premium elegance</div>
            </li>
            <li>
              <strong>Body:</strong> Inter (sans-serif)
              <div className="mt-1 text-text-secondary">Usage: Paragraphs, buttons, UI labels, form inputs</div>
              <div className="mt-1 text-text-secondary">Weight: 400 (regular), 500 (medium), 600 (semi-bold)</div>
            </li>
          </ul>
        </SpecCard>

        <SpecCard>
          <h4 className="mb-3">Type Scale (Do NOT override with Tailwind classes)</h4>
          <div className="space-y-3">
            <div>
              <div className="font-bold mb-1">H1 - Page Titles</div>
              <div className="text-sm text-text-secondary">Font: Playfair Display • Size: Inherited from theme.css • Line Height: 1.2</div>
              <div className="text-sm text-text-secondary">Usage: Homepage hero, main page headers</div>
            </div>
            <div>
              <div className="font-bold mb-1">H2 - Section Headers</div>
              <div className="text-sm text-text-secondary">Font: Playfair Display • Size: Inherited from theme.css • Line Height: 1.3</div>
              <div className="text-sm text-text-secondary">Usage: Whiskey names, quiz section titles</div>
            </div>
            <div>
              <div className="font-bold mb-1">H3 - Card Titles</div>
              <div className="text-sm text-text-secondary">Font: Playfair Display • Size: Inherited from theme.css • Line Height: 1.4</div>
              <div className="text-sm text-text-secondary">Usage: Feature cards, whiskey card titles</div>
            </div>
            <div>
              <div className="font-bold mb-1">H4 - Subsection Titles</div>
              <div className="text-sm text-text-secondary">Font: Playfair Display • Size: Inherited from theme.css • Line Height: 1.4</div>
              <div className="text-sm text-text-secondary">Usage: Quiz instructions, card subtitles</div>
            </div>
            <div>
              <div className="font-bold mb-1">Body Text</div>
              <div className="text-sm text-text-secondary">Font: Inter • Size: 14-16px • Line Height: 1.6</div>
              <div className="text-sm text-text-secondary">Usage: Descriptions, instructions, general content</div>
            </div>
            <div>
              <div className="font-bold mb-1">Small Text</div>
              <div className="text-sm text-text-secondary">Font: Inter • Size: 12-14px • Line Height: 1.5</div>
              <div className="text-sm text-text-secondary">Usage: Metadata, labels, secondary information</div>
            </div>
          </div>
        </SpecCard>

        <SpecCard>
          <h4 className="mb-3">Critical Typography Rules</h4>
          <ul className="space-y-2 text-sm text-text-secondary">
            <li>❌ <strong>NEVER</strong> use Tailwind font-size classes (text-xl, text-2xl, etc.)</li>
            <li>❌ <strong>NEVER</strong> use Tailwind font-weight classes (font-bold, font-semibold, etc.) on headings</li>
            <li>❌ <strong>NEVER</strong> use Tailwind line-height classes (leading-tight, leading-loose, etc.)</li>
            <li>✅ <strong>ALWAYS</strong> rely on default styles from /src/styles/theme.css</li>
            <li>✅ <strong>ONLY</strong> override if user specifically requests style changes</li>
          </ul>
        </SpecCard>
      </Section>

      {/* Spacing & Layout */}
      <Section title="Spacing & Layout">
        <SpecCard>
          <h4 className="mb-3">Container Specifications</h4>
          <ul className="space-y-2 text-sm">
            <li><strong>Max Width:</strong> 480px (enforced mobile-first design)</li>
            <li><strong>Centered:</strong> mx-auto for desktop viewing</li>
            <li><strong>Horizontal Padding:</strong> px-5 (20px) on main content</li>
            <li><strong>Vertical Spacing:</strong> space-y-6 (24px) between major sections</li>
            <li><strong>Bottom Padding:</strong> pb-8 (32px) for scroll clearance</li>
          </ul>
        </SpecCard>

        <SpecCard>
          <h4 className="mb-3">Touch Target Sizing</h4>
          <ul className="space-y-2 text-sm">
            <li><strong>Minimum Height:</strong> 44px for all interactive elements</li>
            <li><strong>Button Height:</strong> 48-56px for primary actions</li>
            <li><strong>Tab Buttons:</strong> 56px minimum height (Nose/Palate/Finish)</li>
            <li><strong>Flavor Grid Buttons:</strong> 80px minimum height</li>
            <li><strong>Card Padding:</strong> lg = 24px, md = 16px, sm = 12px</li>
          </ul>
        </SpecCard>
      </Section>

      {/* Component Specifications */}
      <Section title="Component Specifications">
        
        <SpecCard>
          <h4 className="mb-4">Card Component</h4>
          <div className="space-y-3 text-sm">
            <div>
              <strong>Variants:</strong>
              <ul className="ml-4 mt-1 space-y-1 text-text-secondary">
                <li>• <strong>default:</strong> White background, subtle shadow, rounded corners</li>
                <li>• <strong>bordered:</strong> Border instead of shadow, more subtle</li>
              </ul>
            </div>
            <div>
              <strong>Padding Options:</strong>
              <ul className="ml-4 mt-1 space-y-1 text-text-secondary">
                <li>• <strong>sm:</strong> 12px - Compact content</li>
                <li>• <strong>md:</strong> 16px - Standard cards</li>
                <li>• <strong>lg:</strong> 24px - Feature cards, forms</li>
              </ul>
            </div>
            <div>
              <strong>Interactive States:</strong>
              <ul className="ml-4 mt-1 space-y-1 text-text-secondary">
                <li>• Clickable cards have cursor-pointer</li>
                <li>• Hover: Subtle shadow increase (0 2px 8px → 0 4px 16px)</li>
                <li>• Transition: all 200ms ease-in-out</li>
              </ul>
            </div>
          </div>
        </SpecCard>

        <SpecCard>
          <h4 className="mb-4">Button Component</h4>
          <div className="space-y-3 text-sm">
            <div>
              <strong>Variants:</strong>
              <ul className="ml-4 mt-1 space-y-1 text-text-secondary">
                <li>• <strong>primary:</strong> Navy gradient background, gold text, 48px height</li>
                <li>• <strong>secondary:</strong> White background, navy border, navy text</li>
                <li>• <strong>outline:</strong> Transparent background, navy border</li>
              </ul>
            </div>
            <div>
              <strong>States:</strong>
              <ul className="ml-4 mt-1 space-y-1 text-text-secondary">
                <li>• <strong>Default:</strong> Full opacity, pointer cursor</li>
                <li>• <strong>Hover:</strong> opacity: 0.9, subtle shadow</li>
                <li>• <strong>Disabled:</strong> opacity: 0.5, cursor: not-allowed, no hover effects</li>
                <li>• <strong>Active:</strong> transform: scale(0.98), quick transition</li>
              </ul>
            </div>
            <div>
              <strong>Typography:</strong>
              <ul className="ml-4 mt-1 space-y-1 text-text-secondary">
                <li>• Font: Inter, 14-16px</li>
                <li>• Weight: 600 (semi-bold)</li>
                <li>• Full width on mobile, auto width on desktop</li>
              </ul>
            </div>
          </div>
        </SpecCard>

        <SpecCard>
          <h4 className="mb-4">Badge Component</h4>
          <div className="space-y-3 text-sm">
            <div>
              <strong>Variants:</strong>
              <ul className="ml-4 mt-1 space-y-1 text-text-secondary">
                <li>• <strong>primary:</strong> Navy background, gold text, for featured items</li>
                <li>• <strong>success:</strong> Green background, white text, for correct answers</li>
                <li>• <strong>error:</strong> Red background, white text, for incorrect answers</li>
                <li>• <strong>warning:</strong> Orange background, white text, for alerts</li>
              </ul>
            </div>
            <div>
              <strong>Sizing:</strong>
              <ul className="ml-4 mt-1 space-y-1 text-text-secondary">
                <li>• Padding: 6px 12px</li>
                <li>• Font size: 12px</li>
                <li>• Border radius: 16px (pill shape)</li>
                <li>• Font weight: 600</li>
              </ul>
            </div>
          </div>
        </SpecCard>

        <SpecCard>
          <h4 className="mb-4">SearchBar Component</h4>
          <div className="space-y-3 text-sm">
            <div>
              <strong>Design:</strong>
              <ul className="ml-4 mt-1 space-y-1 text-text-secondary">
                <li>• Height: 48px minimum</li>
                <li>• Search icon on left (16px)</li>
                <li>• Clear (X) icon on right when value exists</li>
                <li>• Border: 2px solid neutral-light</li>
                <li>• Focus state: Border becomes primary navy</li>
              </ul>
            </div>
            <div>
              <strong>Behavior:</strong>
              <ul className="ml-4 mt-1 space-y-1 text-text-secondary">
                <li>• Real-time filtering as user types</li>
                <li>• Clear button removes all text instantly</li>
                <li>• Placeholder text in text-secondary color</li>
                <li>• Auto-focus on mobile when card is tapped (optional)</li>
              </ul>
            </div>
          </div>
        </SpecCard>
      </Section>

      {/* Page-Specific UX Behavior */}
      <Section title="Page-Specific UX Behavior">
        
        <SpecCard>
          <h4 className="mb-4">1. HOME SCREEN</h4>
          <div className="space-y-4 text-sm">
            <div>
              <strong className="block mb-2">Layout Structure:</strong>
              <ol className="ml-4 space-y-2 text-text-secondary">
                <li>1. <strong>Highlighted Whiskey Card</strong> - Featured daily challenge at top</li>
                <li>2. <strong>Distillery Library Card</strong> - Navigation to full whiskey collection</li>
                <li>3. <strong>Search for a Whiskey Card</strong> - Inline search at bottom</li>
              </ol>
            </div>
            
            <div>
              <strong className="block mb-2">Highlighted Whiskey Behavior:</strong>
              <ul className="ml-4 space-y-1 text-text-secondary">
                <li>• Displays: Whiskey name (Eagle Rare 10 Year), distillery, proof</li>
                <li>• "Featured" badge in top-right</li>
                <li>• Gold star icon with challenge details</li>
                <li>• Tap anywhere on card → Navigate to Quiz screen</li>
                <li>• Hover effect: Shadow increases, cursor pointer</li>
              </ul>
            </div>

            <div>
              <strong className="block mb-2">Distillery Library Behavior:</strong>
              <ul className="ml-4 space-y-1 text-text-secondary">
                <li>• Single card navigation element</li>
                <li>• Shows "500+ professional reviews" count</li>
                <li>• Tap anywhere → Navigate to Library screen</li>
                <li>• Does NOT move when search results expand below</li>
              </ul>
            </div>

            <div>
              <strong className="block mb-2">Search for a Whiskey Behavior:</strong>
              <ul className="ml-4 space-y-1 text-text-secondary">
                <li>• Initially shows empty search bar</li>
                <li>• No results shown until user types</li>
                <li>• As user types: Results appear below search bar</li>
                <li>• Results container: max-height 300px, overflow-y scroll</li>
                <li>• Each result shows: Name, Distillery • Proof, Type</li>
                <li>• Tap result → Navigate to quiz for that whiskey</li>
                <li>• Empty state: "No whiskeys found matching [query]"</li>
                <li>• Position at bottom prevents pushing library card down</li>
              </ul>
            </div>
          </div>
        </SpecCard>

        <SpecCard>
          <h4 className="mb-4">2. QUIZ SCREEN</h4>
          <div className="space-y-4 text-sm">
            <div>
              <strong className="block mb-2">Header Behavior:</strong>
              <ul className="ml-4 space-y-1 text-text-secondary">
                <li>• Shows whiskey name centered (Eagle Rare 10 Year)</li>
                <li>• Subtitle: "Identify the flavor notes from the professional review"</li>
                <li>• "HOME" text button in top-left (navy accent color) → Returns to home screen</li>
                <li>• Hamburger menu in top-right</li>
              </ul>
            </div>

            <div>
              <strong className="block mb-2">Category Navigation (Nose/Palate/Finish):</strong>
              <ul className="ml-4 space-y-1 text-text-secondary">
                <li>• Three equal-width buttons in grid (grid-cols-3)</li>
                <li>• Minimum height: 56px for comfortable tapping</li>
                <li>• Active state: Navy gradient background, gold text, gold border, shadow</li>
                <li>• Inactive state: White/cream background, dark text, light border</li>
                <li>• Tap behavior: Instantly switch category, preserve previous selections</li>
                <li>• Transitions: Smooth 200ms for all state changes</li>
                <li>• Font: Playfair Display, 16px, 600 weight</li>
              </ul>
            </div>

            <div>
              <strong className="block mb-2">Quiz Card Behavior:</strong>
              <ul className="ml-4 space-y-1 text-text-secondary">
                <li>• <strong>Header Section (bordered bottom):</strong></li>
                <li>&nbsp;&nbsp;- Whiskey name as h3 (Playfair Display)</li>
                <li>&nbsp;&nbsp;- Distillery: [name] (medium weight label)</li>
                <li>&nbsp;&nbsp;- Proof: [value] (medium weight label)</li>
                <li>&nbsp;&nbsp;- 5px padding below, border separator</li>
                <li>• <strong>Instruction Text:</strong> "Select all flavor notes mentioned in the review:"</li>
                <li>• <strong>Flavor Grid:</strong> 3x3 grid (grid-cols-3), gap-3</li>
                <li>• <strong>Submit Button:</strong> Disabled until at least one selection made</li>
              </ul>
            </div>

            <div>
              <strong className="block mb-2">Flavor Button Behavior:</strong>
              <ul className="ml-4 space-y-1 text-text-secondary">
                <li>• Minimum height: 80px for easy tapping</li>
                <li>• Unselected: White background, light gray border, dark text</li>
                <li>• Selected: Navy background, navy border, white text</li>
                <li>• Toggle on tap: Add/remove from selections</li>
                <li>• Transition: 200ms smooth for background, border, color</li>
                <li>• Font: Inter, 14px, medium weight, centered</li>
                <li>• Multi-select allowed (user can pick multiple)</li>
              </ul>
            </div>

            <div>
              <strong className="block mb-2">State Persistence:</strong>
              <ul className="ml-4 space-y-1 text-text-secondary">
                <li>• Each category (Nose/Palate/Finish) stores selections independently</li>
                <li>• Switching between categories preserves previous selections</li>
                <li>• Selections remain visible when returning to a category</li>
                <li>• Submit button only submits current category's selections</li>
              </ul>
            </div>

            <div>
              <strong className="block mb-2">Submit Behavior:</strong>
              <ul className="ml-4 space-y-1 text-text-secondary">
                <li>• Tap "Submit Answer" → Shows success message card</li>
                <li>• Success card: Green text, "Answer Submitted!" heading</li>
                <li>• Encouragement text: "Great job! Let's move on to the next question."</li>
                <li>• Submit enables "Next" button</li>
              </ul>
            </div>

            <div>
              <strong className="block mb-2">Navigation Controls:</strong>
              <ul className="ml-4 space-y-1 text-text-secondary">
                <li>• Two buttons: "← Previous" (left) and "Next →" (right)</li>
                <li>• Previous disabled on Nose category</li>
                <li>• Next always enabled (can skip without submitting)</li>
                <li>• Flow: Nose → Palate → Finish → Quiz Results</li>
                <li>• Previous reverses the flow</li>
              </ul>
            </div>
          </div>
        </SpecCard>

        <SpecCard>
          <h4 className="mb-4">3. QUIZ RESULTS SCREEN</h4>
          <div className="space-y-4 text-sm">
            <div>
              <strong className="block mb-2">Header Section:</strong>
              <ul className="ml-4 space-y-1 text-text-secondary">
                <li>• Large heading: "Your Results"</li>
                <li>• Whiskey name: "Buffalo Trace Kentucky Straight Bourbon"</li>
                <li>• Metadata row: "Buffalo Trace Distillery • 90 Proof • No Age Statement"</li>
                <li>• Overall score: Large display (e.g., "6/10 Correct")</li>
                <li>• Percentage display in gold accent color</li>
              </ul>
            </div>

            <div>
              <strong className="block mb-2">Results Cards (3 cards: Nose, Palate, Finish):</strong>
              <ul className="ml-4 space-y-1 text-text-secondary">
                <li>• Each card has sense name as header (Playfair Display)</li>
                <li>• Score display: "[correct]/[total] Correct"</li>
                <li>• Percentage badge on right (green if ≥70%, red if &lt;70%)</li>
                <li>• Descriptors grid: 3x3 layout matching quiz screen</li>
                <li>• Color coding:</li>
                <li>&nbsp;&nbsp;- Green background: Correct answer, user selected it ✓</li>
                <li>&nbsp;&nbsp;- Red background: User selected it but it was wrong ✗</li>
                <li>&nbsp;&nbsp;- Green border only: Correct answer, user missed it</li>
                <li>&nbsp;&nbsp;- Gray: Not correct, user didn't select</li>
              </ul>
            </div>

            <div>
              <strong className="block mb-2">Action Buttons:</strong>
              <ul className="ml-4 space-y-1 text-text-secondary">
                <li>• "View Full Review" - Opens review modal/page</li>
                <li>• "Take Another Quiz" - Returns to home screen</li>
                <li>• "Back to Home" - Returns to home screen</li>
                <li>• Buttons stack vertically on mobile</li>
                <li>• Primary button styling for main CTA</li>
              </ul>
            </div>
          </div>
        </SpecCard>

        <SpecCard>
          <h4 className="mb-4">4. WHISKEY LIBRARY SCREEN</h4>
          <div className="space-y-4 text-sm">
            <div>
              <strong className="block mb-2">Layout:</strong>
              <ul className="ml-4 space-y-1 text-text-secondary">
                <li>• Page title: "Whiskey Library"</li>
                <li>• Search bar at top, always visible</li>
                <li>• Scrollable list of whiskey cards below</li>
              </ul>
            </div>

            <div>
              <strong className="block mb-2">Search Behavior:</strong>
              <ul className="ml-4 space-y-1 text-text-secondary">
                <li>• Real-time filtering as user types</li>
                <li>• Searches whiskey name field only</li>
                <li>• Case-insensitive matching</li>
                <li>• Results update instantly (no submit button)</li>
                <li>• Shows all items when search is empty</li>
              </ul>
            </div>

            <div>
              <strong className="block mb-2">Whiskey Cards:</strong>
              <ul className="ml-4 space-y-1 text-text-secondary">
                <li>• Each card displays: Name, Type (Bourbon/Scotch/Rye)</li>
                <li>• Rating badge: "[number] Points" in primary badge</li>
                <li>• Verified badge if applicable (green success badge)</li>
                <li>• Tap card → Navigate to quiz for that whiskey</li>
                <li>• Padding: md (16px)</li>
                <li>• Space-y-3 between cards</li>
              </ul>
            </div>

            <div>
              <strong className="block mb-2">Empty State:</strong>
              <ul className="ml-4 space-y-1 text-text-secondary">
                <li>• Shows when no results match search query</li>
                <li>• Message: "No whiskeys found matching '[query]'"</li>
                <li>• Centered in card with subtle styling</li>
              </ul>
            </div>
          </div>
        </SpecCard>
      </Section>

      {/* Animation & Transitions */}
      <Section title="Animation & Transitions">
        <SpecCard>
          <h4 className="mb-3">Transition Standards</h4>
          <ul className="space-y-2 text-sm text-text-secondary">
            <li><strong>Default Duration:</strong> 200ms for most interactions</li>
            <li><strong>Easing:</strong> ease-in-out for smooth, natural motion</li>
            <li><strong>Properties:</strong> all, opacity, transform, background-color, border-color, box-shadow</li>
            <li><strong>Hover States:</strong> Subtle changes (opacity, shadow, scale)</li>
            <li><strong>Active States:</strong> scale(0.98) for tactile feedback</li>
            <li><strong>Page Transitions:</strong> Instant (no fade/slide between screens)</li>
          </ul>
        </SpecCard>

        <SpecCard>
          <h4 className="mb-3">Specific Animations</h4>
          <div className="space-y-2 text-sm">
            <div>
              <strong>Button Click:</strong>
              <div className="text-text-secondary ml-4">transform: scale(0.98) on active, 100ms duration</div>
            </div>
            <div>
              <strong>Card Hover:</strong>
              <div className="text-text-secondary ml-4">Shadow: 0 2px 8px → 0 4px 16px, 200ms duration</div>
            </div>
            <div>
              <strong>Flavor Button Selection:</strong>
              <div className="text-text-secondary ml-4">Background, border, color all transition 200ms</div>
            </div>
            <div>
              <strong>Tab Navigation:</strong>
              <div className="text-text-secondary ml-4">Background gradient, border, shadow transition 200ms</div>
            </div>
            <div>
              <strong>Search Results:</strong>
              <div className="text-text-secondary ml-4">Appear instantly, no fade animation</div>
            </div>
          </div>
        </SpecCard>
      </Section>

      {/* Accessibility */}
      <Section title="Accessibility Requirements">
        <SpecCard>
          <h4 className="mb-3">Touch Targets</h4>
          <ul className="space-y-2 text-sm text-text-secondary">
            <li>✅ All interactive elements minimum 44x44px (WCAG 2.1 AAA)</li>
            <li>✅ Buttons 48-56px height for comfortable mobile tapping</li>
            <li>✅ Adequate spacing (12px minimum) between adjacent tappable elements</li>
            <li>✅ Flavor grid buttons 80px minimum height</li>
          </ul>
        </SpecCard>

        <SpecCard>
          <h4 className="mb-3">Color Contrast</h4>
          <ul className="space-y-2 text-sm text-text-secondary">
            <li>✅ Navy (#2a3c93) on cream background meets WCAG AA</li>
            <li>✅ Gold (#d4af37) on navy background meets WCAG AA</li>
            <li>✅ White text on navy/green/red backgrounds meets WCAG AAA</li>
            <li>✅ Dark text (#2d2d2d) on white/cream meets WCAG AAA</li>
          </ul>
        </SpecCard>

        <SpecCard>
          <h4 className="mb-3">Semantic HTML</h4>
          <ul className="space-y-2 text-sm text-text-secondary">
            <li>✅ Use button elements for interactive elements (not divs)</li>
            <li>✅ Proper heading hierarchy (h1 → h2 → h3 → h4)</li>
            <li>✅ aria-label on icon-only buttons</li>
            <li>✅ Disabled state communicated via disabled attribute</li>
          </ul>
        </SpecCard>
      </Section>

      {/* Technical Implementation */}
      <Section title="Technical Implementation">
        <SpecCard>
          <h4 className="mb-3">File Structure</h4>
          <div className="text-sm font-mono bg-background p-4 rounded-lg space-y-1">
            <div>/src/app/App.tsx - Main app, routing, screens</div>
            <div>/src/app/components/</div>
            <div>&nbsp;&nbsp;- Header.tsx - Top navigation bar</div>
            <div>&nbsp;&nbsp;- HamburgerMenu.tsx - Slide-out menu</div>
            <div>&nbsp;&nbsp;- QuizCard.tsx - Quiz interface with flavor grid</div>
            <div>&nbsp;&nbsp;- Card.tsx - Reusable card container</div>
            <div>&nbsp;&nbsp;- Button.tsx - Button variants</div>
            <div>&nbsp;&nbsp;- Badge.tsx - Status badges</div>
            <div>&nbsp;&nbsp;- SearchBar.tsx - Search input with icons</div>
            <div>&nbsp;&nbsp;- QuizResultsScreen.tsx - Results display</div>
            <div>/src/styles/</div>
            <div>&nbsp;&nbsp;- theme.css - CSS custom properties, type scale</div>
            <div>&nbsp;&nbsp;- fonts.css - Font imports (Google Fonts)</div>
          </div>
        </SpecCard>

        <SpecCard>
          <h4 className="mb-3">State Management</h4>
          <ul className="space-y-2 text-sm text-text-secondary">
            <li><strong>Screen Navigation:</strong> Single useState for currentScreen</li>
            <li><strong>Quiz Selections:</strong> Separate state arrays for nose/palate/finish</li>
            <li><strong>Search:</strong> Local useState in each screen component</li>
            <li><strong>Form Inputs:</strong> Controlled components with onChange handlers</li>
            <li><strong>No Global State:</strong> All state lifted to parent or kept local</li>
          </ul>
        </SpecCard>

        <SpecCard>
          <h4 className="mb-3">CSS Architecture</h4>
          <ul className="space-y-2 text-sm text-text-secondary">
            <li><strong>Framework:</strong> Tailwind CSS v4</li>
            <li><strong>Custom Properties:</strong> Defined in theme.css, accessed via var(--property)</li>
            <li><strong>Style Priority:</strong> theme.css defaults → Tailwind utilities → inline styles</li>
            <li><strong>Inline Styles:</strong> Used for dynamic values (colors, state-based styling)</li>
            <li><strong>Responsive:</strong> Mobile-first, max-width container approach</li>
          </ul>
        </SpecCard>

        <SpecCard>
          <h4 className="mb-3">Data Structure Examples</h4>
          <div className="text-sm space-y-3">
            <div>
              <strong>Whiskey Object:</strong>
              <pre className="bg-background p-3 rounded mt-2 text-xs overflow-x-auto">
{`{
  name: 'Eagle Rare 10 Year',
  distillery: 'Buffalo Trace',
  proof: '90 proof',
  type: 'Bourbon',
  age: '10 Year',
  rating: 91,
  verified: true
}`}
              </pre>
            </div>
            <div>
              <strong>Quiz Option:</strong>
              <pre className="bg-background p-3 rounded mt-2 text-xs overflow-x-auto">
{`{
  id: '1',
  label: 'Vanilla'
}`}
              </pre>
            </div>
            <div>
              <strong>Result Descriptor:</strong>
              <pre className="bg-background p-3 rounded mt-2 text-xs overflow-x-auto">
{`{
  label: 'Vanilla',
  isCorrect: true,
  wasSelected: true
}`}
              </pre>
            </div>
          </div>
        </SpecCard>
      </Section>

      {/* Design Tokens */}
      <Section title="CSS Custom Properties Reference">
        <SpecCard>
          <div className="text-sm font-mono space-y-1 bg-background p-4 rounded-lg">
            <div className="text-text-secondary">/* Colors */</div>
            <div>--primary: #2a3c93;</div>
            <div>--primary-dark: #1e2d6e;</div>
            <div>--accent: #d4af37;</div>
            <div>--background: #f5f1e8;</div>
            <div>--card: #ffffff;</div>
            <div>--neutral-dark: #2d2d2d;</div>
            <div>--text-secondary: #666666;</div>
            <div>--neutral-light: #e0d5c7;</div>
            <div>--success: #2e7d32;</div>
            <div>--error: #c62828;</div>
            <div>--warning: #f57c00;</div>
            <div className="text-text-secondary mt-3">/* Typography */</div>
            <div>--font-heading: 'Playfair Display', serif;</div>
            <div>--font-body: 'Inter', sans-serif;</div>
          </div>
        </SpecCard>
      </Section>

      {/* Critical Rules */}
      <Section title="Critical Development Rules">
        <SpecCard>
          <div className="space-y-3">
            <div className="p-3 rounded-lg" style={{ backgroundColor: '#fff3cd', borderLeft: '4px solid #f57c00' }}>
              <h4 className="mb-2" style={{ color: '#856404' }}>⚠️ Typography Override Warning</h4>
              <p className="text-sm" style={{ color: '#856404' }}>
                NEVER use Tailwind classes for font-size, font-weight, or line-height on text elements unless explicitly requested by user. Theme.css handles all default typography.
              </p>
            </div>
            
            <div className="p-3 rounded-lg" style={{ backgroundColor: '#d4edda', borderLeft: '4px solid #2e7d32' }}>
              <h4 className="mb-2" style={{ color: '#155724' }}>✅ Component Reusability</h4>
              <p className="text-sm" style={{ color: '#155724' }}>
                Always use existing components (Card, Button, Badge, etc.) rather than creating custom elements. Maintains consistency across the app.
              </p>
            </div>
            
            <div className="p-3 rounded-lg" style={{ backgroundColor: '#d1ecf1', borderLeft: '4px solid #0c5460' }}>
              <h4 className="mb-2" style={{ color: '#0c5460' }}>📱 Mobile-First Priority</h4>
              <p className="text-sm" style={{ color: '#0c5460' }}>
                Design and test for 375px-480px width first. Desktop is secondary. Max-width container ensures mobile experience on all devices.
              </p>
            </div>
          </div>
        </SpecCard>
      </Section>

      {/* Export Notice */}
      <div className="text-center pt-8 pb-4">
        <p className="text-sm text-text-secondary">
          This specification document is exportable and should be shared with development team, designers, and stakeholders.
        </p>
        <p className="text-xs text-text-secondary mt-2">
          Last updated: February 14, 2026
        </p>
      </div>
    </div>
  );
}

// Helper Components
function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section>
      <h2 className="mb-4 pb-2 border-b" style={{ 
        borderColor: 'var(--neutral-light)',
        fontFamily: 'var(--font-heading)',
        color: 'var(--primary)'
      }}>
        {title}
      </h2>
      <div className="space-y-4">
        {children}
      </div>
    </section>
  );
}

function SpecCard({ children }: { children: React.ReactNode }) {
  return (
    <Card padding="lg" variant="default">
      {children}
    </Card>
  );
}

function ColorSwatch({ color, name, usage }: { color: string; name: string; usage: string }) {
  return (
    <div className="flex items-start gap-3">
      <div 
        className="w-16 h-16 rounded-lg border-2 flex-shrink-0" 
        style={{ 
          backgroundColor: color,
          borderColor: 'var(--neutral-light)'
        }}
      />
      <div className="flex-1 min-w-0">
        <div className="font-semibold text-sm mb-1">{name}</div>
        <div className="font-mono text-xs mb-1" style={{ color: 'var(--text-secondary)' }}>
          {color}
        </div>
        <div className="text-xs" style={{ color: 'var(--text-secondary)' }}>
          {usage}
        </div>
      </div>
    </div>
  );
}
