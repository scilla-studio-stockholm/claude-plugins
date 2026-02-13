interface MobileLayoutProps {
  children: React.ReactNode;
  bg?: string;
}

export function MobileLayout({ children, bg = "bg-surface" }: MobileLayoutProps) {
  return (
    <div className="min-h-screen flex items-start justify-center bg-grey-100 py-8">
      <div
        className={`
          relative w-[375px] min-h-[812px]
          ${bg}
          shadow-xl overflow-hidden
          rounded-[40px] border-[8px] border-grey-800
        `}
      >
        {children}
      </div>
    </div>
  );
}
