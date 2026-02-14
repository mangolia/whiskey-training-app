import React, { useState } from 'react';
import { Button } from './Button';
import { Card } from './Card';
import { Checkbox } from './Checkbox';
import { RadioButton } from './RadioButton';
import { SearchBar } from './SearchBar';
import { Input } from './Input';
import { Badge } from './Badge';
import { StarIcon, FilterIcon } from './Icons';

export function ComponentShowcase() {
  const [checkboxStates, setCheckboxStates] = useState({
    checkbox1: false,
    checkbox2: true,
    checkbox3: false,
  });
  
  const [selectedRadio, setSelectedRadio] = useState('option1');
  const [searchValue, setSearchValue] = useState('');
  const [inputValue, setInputValue] = useState('');
  
  return (
    <div className="space-y-8">
      {/* Buttons Section */}
      <section>
        <h2 className="mb-4">Buttons</h2>
        <div className="space-y-3">
          <Button variant="primary">Primary Button</Button>
          <Button variant="secondary">Secondary Button</Button>
          <Button variant="disabled">Disabled Button</Button>
        </div>
      </section>
      
      {/* Cards Section */}
      <section>
        <h2 className="mb-4">Cards</h2>
        <div className="space-y-3">
          <Card variant="default">
            <h3 className="mb-2">Buffalo Trace</h3>
            <p className="text-sm text-text-secondary mb-3">
              Kentucky Straight Bourbon Whiskey
            </p>
            <div className="flex gap-2">
              <Badge variant="primary">90 Points</Badge>
              <Badge variant="success">Verified</Badge>
            </div>
          </Card>
          
          <Card variant="bordered" padding="lg">
            <div className="flex items-start justify-between mb-3">
              <div>
                <h3 className="mb-1">Flavor Quiz</h3>
                <p className="text-sm text-text-secondary">Test your palate</p>
              </div>
              <StarIcon size={24} color="var(--accent)" filled />
            </div>
            <p className="text-sm mb-4">
              Identify the dominant flavor notes in this whiskey from a professional tasting review.
            </p>
            <Button variant="primary">Start Quiz</Button>
          </Card>
        </div>
      </section>
      
      {/* Form Elements Section */}
      <section>
        <h2 className="mb-4">Form Elements</h2>
        
        <div className="mb-6">
          <h4 className="mb-3 text-sm font-semibold text-neutral-dark">Checkboxes</h4>
          <div className="space-y-2">
            <Checkbox
              label="Caramel"
              checked={checkboxStates.checkbox1}
              onChange={(checked) => setCheckboxStates({ ...checkboxStates, checkbox1: checked })}
            />
            <Checkbox
              label="Vanilla"
              checked={checkboxStates.checkbox2}
              onChange={(checked) => setCheckboxStates({ ...checkboxStates, checkbox2: checked })}
            />
            <Checkbox
              label="Oak"
              checked={checkboxStates.checkbox3}
              onChange={(checked) => setCheckboxStates({ ...checkboxStates, checkbox3: checked })}
            />
          </div>
        </div>
        
        <div className="mb-6">
          <h4 className="mb-3 text-sm font-semibold text-neutral-dark">Radio Buttons</h4>
          <div className="space-y-2">
            <RadioButton
              label="Bourbon"
              name="whiskey-type"
              value="option1"
              checked={selectedRadio === 'option1'}
              onChange={() => setSelectedRadio('option1')}
            />
            <RadioButton
              label="Scotch"
              name="whiskey-type"
              value="option2"
              checked={selectedRadio === 'option2'}
              onChange={() => setSelectedRadio('option2')}
            />
            <RadioButton
              label="Rye"
              name="whiskey-type"
              value="option3"
              checked={selectedRadio === 'option3'}
              onChange={() => setSelectedRadio('option3')}
            />
          </div>
        </div>
        
        <div className="mb-6">
          <h4 className="mb-3 text-sm font-semibold text-neutral-dark">Search Bar</h4>
          <SearchBar
            placeholder="Search whiskey brands..."
            value={searchValue}
            onChange={setSearchValue}
          />
        </div>
        
        <div>
          <h4 className="mb-3 text-sm font-semibold text-neutral-dark">Text Input</h4>
          <div className="space-y-4">
            <Input
              label="Your Name"
              placeholder="Enter your name"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
            />
            <Input
              label="Email Address"
              type="email"
              placeholder="you@example.com"
              error="Please enter a valid email address"
            />
            <Input
              label="Tasting Notes"
              placeholder="Describe what you taste..."
              helperText="Share your impressions"
            />
          </div>
        </div>
      </section>
      
      {/* Badges Section */}
      <section>
        <h2 className="mb-4">Badges</h2>
        <div className="flex flex-wrap gap-2">
          <Badge variant="primary">Featured</Badge>
          <Badge variant="success">Correct</Badge>
          <Badge variant="error">Incorrect</Badge>
          <Badge variant="neutral">Pending</Badge>
        </div>
      </section>
      
      {/* Icons Section */}
      <section>
        <h2 className="mb-4">Icons</h2>
        <div className="flex gap-4 flex-wrap">
          <div className="flex flex-col items-center gap-2">
            <StarIcon size={24} color="var(--accent)" />
            <span className="text-xs text-text-caption">Star</span>
          </div>
          <div className="flex flex-col items-center gap-2">
            <StarIcon size={24} color="var(--accent)" filled />
            <span className="text-xs text-text-caption">Star Filled</span>
          </div>
          <div className="flex flex-col items-center gap-2">
            <FilterIcon size={24} color="var(--neutral-dark)" />
            <span className="text-xs text-text-caption">Filter</span>
          </div>
        </div>
      </section>
    </div>
  );
}
