# Product Guidelines - LaTeX Resume Generator

## Voice & Tone
- **Professional & Minimalist**: Documentation, CLI messages, and logs should be precise, efficient, and direct. Avoid unnecessary jargon or overly verbose explanations. Maintain a "Senior Engineer" vibe—authoritative but accessible.

## Visual Branding & Design
- **Modern & Clean**: Templates should prioritize clean layouts, generous whitespace, and modern sans-serif or crisp serif typography. The visual identity should reflect a contemporary, professional aesthetic suitable for the modern job market.

## User Experience (UX) Principles
- **Configuration First**: The YAML input is the strict single source of truth for all data and configuration. Users should be able to control every aspect of their document through structured data without modifying LaTeX source directly.
- **Safety & Privacy First**: Prioritize robust character escaping and clear privacy warnings. The separation of PII and professional data must be intuitive and fail-safe.

## Technical Standards
- **ATS Optimality**: Machine-readability is the primary technical priority. Documents must be optimized for parsing by modern Applicant Tracking Systems (ATS) while maintaining high visual quality for human readers.
