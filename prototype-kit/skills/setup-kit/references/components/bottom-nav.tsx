export interface BottomNavItem {
  label: string;
  icon: React.ReactNode;
  active?: boolean;
  onPress?: () => void;
}

interface BottomNavProps {
  items: BottomNavItem[];
  homeIndicator?: boolean;
}

export function BottomNav({ items, homeIndicator = true }: BottomNavProps) {
  return (
    <nav className="relative bg-surface border-t border-black/30 backdrop-blur-[25px]">
      <div className="flex justify-between px-0 pt-[7px] h-[49px]">
        {items.map((item) => (
          <button
            key={item.label}
            onClick={item.onPress}
            className={`
              flex flex-1 flex-col items-center gap-[3px]
              ${item.active
                ? "text-accent-fg font-semibold"
                : "text-foreground-secondary font-normal"
              }
            `}
          >
            <span className="size-[21px] flex items-center justify-center">
              {item.icon}
            </span>
            <span className="text-xs leading-4">{item.label}</span>
          </button>
        ))}
      </div>
      {homeIndicator && (
        <div className="h-[34px] flex items-end justify-center pb-2">
          <div className="w-[134px] h-[5px] bg-grey-950 rounded-full" />
        </div>
      )}
    </nav>
  );
}
