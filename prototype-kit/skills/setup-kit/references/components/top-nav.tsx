interface TopNavProps {
  title: string;
  leftAction?: React.ReactNode;
  rightAction?: React.ReactNode;
  transparent?: boolean;
}

export function TopNav({ title, leftAction, rightAction, transparent = false }: TopNavProps) {
  return (
    <nav
      className={`
        flex items-center h-14 px-4 gap-4
        ${transparent ? "bg-transparent" : "bg-accent-surface"}
      `}
    >
      {leftAction && (
        <div className="shrink-0">{leftAction}</div>
      )}
      <h1 className="flex-1 text-2xl leading-7 font-bold text-foreground truncate">
        {title}
      </h1>
      {rightAction && (
        <div className="shrink-0">{rightAction}</div>
      )}
    </nav>
  );
}

export function IconButton({
  children,
  onClick,
  className = "",
}: {
  children: React.ReactNode;
  onClick?: () => void;
  className?: string;
}) {
  return (
    <button
      onClick={onClick}
      className={`
        relative size-10 flex items-center justify-center
        bg-surface rounded-full
        text-foreground
        ${className}
      `}
    >
      {children}
    </button>
  );
}
