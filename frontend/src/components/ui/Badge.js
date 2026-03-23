export default function Badge({ variant = 'default', children, className = '' }) {
  const variants = {
    default:    'bg-slate-100 text-slate-600',
    verified:   'bg-emerald-100 text-emerald-700',
    pending:    'bg-amber-100 text-amber-700',
    rejected:   'bg-red-100 text-red-600',
    tag:        'bg-blue-50 text-blue-700 hover:bg-blue-100 cursor-pointer',
  };

  return (
    <span
      className={`
        inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
        ${variants[variant]}
        ${className}
      `}
    >
      {children}
    </span>
  );
}