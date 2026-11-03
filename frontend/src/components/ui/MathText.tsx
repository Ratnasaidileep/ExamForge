import React from 'react';
import katex from 'katex';

interface MathTextProps {
  text: string | null | undefined;
  className?: string;
}

export const MathText: React.FC<MathTextProps> = ({ text, className = '' }) => {
  if (!text) return null;

  // If there are no '$' characters, return text directly
  if (!text.includes('$')) {
    return <span className={className}>{text}</span>;
  }

  // Regex to split by $$...$$ (block) and $...$ (inline)
  // Handles escaped dollar signs \$ if needed
  const regex = /(\$\$[\s\S]+?\$\$|\$(?:\\.|[^\$\\\n])+\$)/g;
  const parts = text.split(regex);

  return (
    <span className={`math-text-container ${className}`}>
      {parts.map((part, index) => {
        if (!part) return null;

        // Block LaTeX $$...$$
        if (part.startsWith('$$') && part.endsWith('$$') && part.length >= 4) {
          const formula = part.slice(2, -2).trim();
          try {
            const html = katex.renderToString(formula, {
              displayMode: true,
              throwOnError: false,
            });
            return (
              <span
                key={index}
                className="block my-2 overflow-x-auto text-center"
                dangerouslySetInnerHTML={{ __html: html }}
              />
            );
          } catch {
            return <code key={index} className="text-red-600">{part}</code>;
          }
        }

        // Inline LaTeX $...$
        if (part.startsWith('$') && part.endsWith('$') && part.length >= 2) {
          const formula = part.slice(1, -1).trim();
          try {
            const html = katex.renderToString(formula, {
              displayMode: false,
              throwOnError: false,
            });
            return (
              <span
                key={index}
                className="inline-math inline-block align-middle mx-0.5"
                dangerouslySetInnerHTML={{ __html: html }}
              />
            );
          } catch {
            return <code key={index} className="text-red-600">{part}</code>;
          }
        }

        // Regular text
        return <span key={index}>{part}</span>;
      })}
    </span>
  );
};
