/**
 * Centralized chart theme configuration for Recharts.
 * All charts use these tokens so they automatically adapt to dark/light mode.
 * Colors reference CSS custom properties defined in globals.css.
 */

export const CHART_COLORS = {
  blue: "var(--chart-blue)",
  cyan: "var(--chart-cyan)",
  emerald: "var(--chart-emerald)",
  amber: "var(--chart-amber)",
  rose: "var(--chart-rose)",
  violet: "var(--chart-violet)",
  orange: "var(--chart-orange)",
  teal: "var(--chart-teal)",
} as const;

/** Ordered palette for multi-series charts */
export const CHART_PALETTE = [
  CHART_COLORS.blue,
  CHART_COLORS.emerald,
  CHART_COLORS.amber,
  CHART_COLORS.rose,
  CHART_COLORS.violet,
  CHART_COLORS.cyan,
  CHART_COLORS.orange,
  CHART_COLORS.teal,
];

/** Named semantic colors for specific data types */
export const SERIES_COLORS = {
  observed: CHART_COLORS.emerald,
  forecast: CHART_COLORS.blue,
  uncertainty: CHART_COLORS.blue,
  baseline: CHART_COLORS.amber,
  provider: CHART_COLORS.violet,
  error: CHART_COLORS.rose,
  temperature: CHART_COLORS.orange,
  rainfall: CHART_COLORS.blue,
  rainProbability: CHART_COLORS.cyan,
  wind: CHART_COLORS.teal,
  humidity: CHART_COLORS.violet,
  pressure: CHART_COLORS.amber,
} as const;

/** Common axis/grid configuration */
export const CHART_AXIS_STYLE = {
  stroke: "var(--chart-grid)",
  fontSize: 11,
  fontFamily: "var(--font-sans)",
  fill: "var(--chart-text)",
};

/** Tooltip configuration */
export const CHART_TOOLTIP_STYLE = {
  contentStyle: {
    backgroundColor: "var(--chart-tooltip-bg)",
    border: "1px solid var(--chart-tooltip-border)",
    borderRadius: "0.5rem",
    fontSize: "12px",
    color: "var(--chart-tooltip-text)",
    boxShadow: "0 4px 12px rgba(0, 0, 0, 0.15)",
  },
  labelStyle: {
    color: "var(--chart-tooltip-text)",
    fontWeight: 600,
    marginBottom: "4px",
  },
  itemStyle: {
    color: "var(--chart-tooltip-text)",
    fontSize: "11px",
  },
};

/** Area fill opacities */
export const CHART_AREA = {
  fillOpacity: 0.1,
  uncertaintyFillOpacity: 0.15,
};

/** Common chart margins */
export const CHART_MARGIN = {
  top: 8,
  right: 16,
  left: 0,
  bottom: 4,
};

/** Responsive breakpoints for chart height */
export function chartHeight(variant: "sm" | "md" | "lg" = "md"): number {
  switch (variant) {
    case "sm": return 200;
    case "md": return 280;
    case "lg": return 360;
  }
}
