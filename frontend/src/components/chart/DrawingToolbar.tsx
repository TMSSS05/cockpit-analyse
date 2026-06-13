"use client";

// Built-in overlay names used by klinecharts createOverlay()
// The library doesn't export them as a type, so we use string.
export type OverlayName = string;

export type DrawingTool =
  | "cursor"
  | "fibonacci"
  | "trend"
  | "horizontal"
  | "vertical"
  | "ray"
  | "channel"
  | "annotation"
  | "long"
  | "short";

export function toolToOverlay(tool: DrawingTool): OverlayName | null {
  switch (tool) {
    case "fibonacci":
      return "fibonacciLine";
    case "trend":
      return "segment";
    case "horizontal":
      return "horizontalStraightLine";
    case "vertical":
      return "verticalStraightLine";
    case "ray":
      return "rayLine";
    case "channel":
      return "parallelStraightLine";
    case "annotation":
      return "simpleAnnotation";
    default:
      return null;
  }
}

export function toolDrawsOverlay(tool: DrawingTool): boolean {
  return toolToOverlay(tool) !== null;
}

const tools: { id: DrawingTool; label: string }[] = [
  { id: "cursor", label: "Cursor" },
  { id: "fibonacci", label: "Fib" },
  { id: "trend", label: "Trend" },
  { id: "horizontal", label: "H-Line" },
  { id: "vertical", label: "V-Line" },
  { id: "ray", label: "Ray" },
  { id: "channel", label: "Channel" },
  { id: "annotation", label: "Note" },
  { id: "long", label: "Long" },
  { id: "short", label: "Short" },
];

interface DrawingToolbarProps {
  activeTool: DrawingTool;
  onSelectTool: (tool: DrawingTool) => void;
}

export default function DrawingToolbar({
  activeTool,
  onSelectTool,
}: DrawingToolbarProps) {
  return (
    <div className="flex items-center gap-0.5 bg-zinc-900 border border-zinc-700 rounded-md px-1.5 py-1 select-none">
      {tools.map((t) => {
        const isActive = activeTool === t.id;
        return (
          <button
            key={t.id}
            onClick={() => onSelectTool(t.id)}
            className={[
              "px-2 py-1 text-xs font-medium rounded transition-colors",
              isActive
                ? "bg-blue-600 text-white"
                : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800",
            ].join(" ")}
          >
            {t.label}
          </button>
        );
      })}
    </div>
  );
}
