import React from 'react';
import { Card } from './Card';
import { Badge } from './Badge';
import { CheckmarkIcon } from './Icons';
import { X } from 'lucide-react';

interface ResultCardProps {
  correct: boolean;
  score: number;
  totalQuestions: number;
  correctAnswers?: string[];
  yourAnswers?: string[];
  message?: string;
}

export function ResultCard({ 
  correct, 
  score, 
  totalQuestions,
  correctAnswers = [],
  yourAnswers = [],
  message 
}: ResultCardProps) {
  const percentage = Math.round((score / totalQuestions) * 100);
  
  return (
    <Card 
      padding="lg" 
      className="mb-4"
      variant="bordered"
    >
      <div className="text-center mb-6">
        <div 
          className="w-20 h-20 rounded-full mx-auto mb-4 flex items-center justify-center"
          style={{ 
            backgroundColor: correct ? 'var(--success)' : 'var(--error)',
            opacity: 0.1 
          }}
        >
          {correct ? (
            <CheckmarkIcon size={40} color="var(--success)" />
          ) : (
            <X size={40} strokeWidth={2.5} color="var(--error)" />
          )}
        </div>
        
        <h2 className="mb-2" style={{ color: correct ? 'var(--success)' : 'var(--error)' }}>
          {correct ? 'Correct!' : 'Not Quite'}
        </h2>
        
        <p className="text-lg mb-4 text-neutral-dark">
          Score: {score} / {totalQuestions}
        </p>
        
        <Badge variant={percentage >= 70 ? 'success' : percentage >= 50 ? 'primary' : 'error'}>
          {percentage}% Accuracy
        </Badge>
      </div>
      
      {message && (
        <p className="text-sm text-text-secondary text-center mb-6">
          {message}
        </p>
      )}
      
      {correctAnswers.length > 0 && (
        <div className="space-y-4 pt-4 border-t border-neutral-light">
          <div>
            <h4 className="text-sm font-semibold text-success mb-2">Correct Answers:</h4>
            <div className="flex flex-wrap gap-2">
              {correctAnswers.map((answer, idx) => (
                <Badge key={idx} variant="success">{answer}</Badge>
              ))}
            </div>
          </div>
          
          {yourAnswers.length > 0 && (
            <div>
              <h4 className="text-sm font-semibold text-neutral-dark mb-2">Your Answers:</h4>
              <div className="flex flex-wrap gap-2">
                {yourAnswers.map((answer, idx) => (
                  <Badge 
                    key={idx} 
                    variant={correctAnswers.includes(answer) ? 'success' : 'error'}
                  >
                    {answer}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </Card>
  );
}
