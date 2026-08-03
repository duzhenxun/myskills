import {
  AbsoluteFill,
  Easing,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

const data = [
  {label: "North", value: 72, color: "#2563eb"},
  {label: "South", value: 48, color: "#10b981"},
  {label: "East", value: 86, color: "#f59e0b"},
  {label: "West", value: 63, color: "#ef4444"},
  {label: "Central", value: 94, color: "#7c3aed"},
];

const maxValue = Math.max(...data.map((item) => item.value));

export const AnimatedBars = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const titleOpacity = interpolate(frame, [0, fps * 0.7], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });

  const ruleProgress = interpolate(frame, [fps * 0.4, fps * 1.6], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });

  return (
    <AbsoluteFill
      style={{
        background: "#f8fafc",
        color: "#111827",
        fontFamily:
          "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",
        padding: 80,
      }}
    >
      <div
        style={{
          opacity: titleOpacity,
          transform: `translateY(${interpolate(titleOpacity, [0, 1], [18, 0])}px)`,
        }}
      >
        <div
          style={{
            color: "#64748b",
            fontSize: 24,
            fontWeight: 700,
            letterSpacing: 0,
            marginBottom: 12,
            textTransform: "uppercase",
          }}
        >
          Regional revenue
        </div>
        <h1
          style={{
            fontSize: 68,
            lineHeight: 1,
            margin: 0,
          }}
        >
          Animated 5-bar chart
        </h1>
      </div>

      <div
        style={{
          alignItems: "end",
          display: "grid",
          gap: 34,
          gridTemplateColumns: "repeat(5, 1fr)",
          height: 390,
          marginTop: 72,
          position: "relative",
        }}
      >
        <div
          style={{
            background: "#cbd5e1",
            height: 3,
            left: 0,
            opacity: 0.8,
            position: "absolute",
            right: `${(1 - ruleProgress) * 100}%`,
            top: 72,
          }}
        />
        {data.map((item, index) => {
          const scale = spring({
            frame,
            fps,
            delay: 9 + index * 5,
            config: {
              damping: 18,
              mass: 0.75,
              stiffness: 95,
            },
          });

          const labelOpacity = interpolate(
            frame,
            [fps * 1.1 + index * 4, fps * 1.7 + index * 4],
            [0, 1],
            {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            },
          );

          const height = (item.value / maxValue) * 330 * scale;

          return (
            <div
              key={item.label}
              style={{
                alignItems: "center",
                display: "flex",
                flexDirection: "column",
                height: "100%",
                justifyContent: "end",
                minWidth: 0,
              }}
            >
              <div
                style={{
                  color: "#111827",
                  fontSize: 32,
                  fontWeight: 800,
                  marginBottom: 18,
                  opacity: labelOpacity,
                }}
              >
                {item.value}
              </div>
              <div
                style={{
                  background: item.color,
                  borderRadius: "8px 8px 0 0",
                  boxShadow: `0 24px 40px ${item.color}33`,
                  height,
                  width: "100%",
                }}
              />
              <div
                style={{
                  color: "#475569",
                  fontSize: 26,
                  fontWeight: 700,
                  marginTop: 20,
                  opacity: labelOpacity,
                  textAlign: "center",
                  width: "100%",
                }}
              >
                {item.label}
              </div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
