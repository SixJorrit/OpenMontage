import React from "react";
import { AbsoluteFill } from "remotion";
import type { TransitionPresentation, TransitionPresentationComponentProps } from "@remotion/transitions";

/**
 * Star Wars-achtige wipes met een zichtbare rand die de grens volgt (Jorrit 2026-10-12: "trager, dikkere border,
 * of iets dat de transitie volgt"). Zachte in-uit-versnelling; de band/wijzer wordt alleen op het binnenkomende shot getekend.
 */
export type BandWipeProps = {
  kind: "linear" | "clock";
  direction?: "from-left" | "from-right";
  width: number; height: number;
  band?: number;           // breedte van de gloeiband in px
  color?: string;          // kleur van de band
  solid?: boolean;         // egale balk zonder verloop/gloed (Jorrit: "zwart en een simpele vorm")
  look?: "bar" | "line" | "shadow" | "none";   // subtielere varianten (Jorrit: "moet toch subtieler")
  opacity?: number;
};
const ease = (p: number) => 0.5 - 0.5 * Math.cos(Math.PI * Math.min(Math.max(p, 0), 1));

const BandWipeComponent: React.FC<TransitionPresentationComponentProps<BandWipeProps>> = ({
  children, presentationDirection, presentationProgress, passedProps,
}) => {
  if (presentationDirection === "exiting") return <AbsoluteFill>{children}</AbsoluteFill>;
  const { kind, direction = "from-right", width: W, height: H, band = 26, color = "#000000", solid = true, look = "bar", opacity = 1 } = passedProps;
  const p = ease(presentationProgress);
  const glow = solid ? "none" : `0 0 ${band * 0.9}px ${band * 0.35}px ${color}, 0 0 ${band * 0.35}px ${band * 0.15}px #ffffff`;
  const fill = (deg: number) => look === "shadow"
    ? `linear-gradient(${deg}deg, rgba(0,0,0,0) 0%, rgba(0,0,0,0.55) 50%, rgba(0,0,0,0) 100%)`
    : solid ? color
    : `linear-gradient(${deg}deg, rgba(255,255,255,0) 0%, ${color} 30%, #FFF6D8 50%, ${color} 70%, rgba(255,255,255,0) 100%)`;
  if (kind === "linear") {
    // grens loopt van buiten het beeld aan de ene kant naar buiten het beeld aan de andere kant
    const span = W + band * 2;
    const edge = direction === "from-right" ? W + band - p * span : -band + p * span;
    const clip = direction === "from-right" ? `inset(0 0 0 ${Math.max(edge, 0)}px)` : `inset(0 ${Math.max(W - edge, 0)}px 0 0)`;
    return (
      <AbsoluteFill>
        <AbsoluteFill style={{ clipPath: clip }}>{children}</AbsoluteFill>
        <div style={{ position: "absolute", top: -20, height: H + 40, left: edge - band / 2, width: band,
          background: fill(90),
          boxShadow: glow, opacity: look === "none" || p < 0.02 || p > 0.98 ? 0 : opacity }} />
      </AbsoluteFill>
    );
  }
  // klok-wipe: sector vanaf 12 uur met de klok mee; gloeiende wijzer op de rand
  const cx = W / 2, cy = H / 2, R = Math.hypot(W, H);
  const theta = p * 360; const pts: string[] = [`${cx}px ${cy}px`];
  for (let a = 0; a <= theta; a += 3) { const r = (a - 90) * Math.PI / 180; pts.push(`${cx + R * Math.cos(r)}px ${cy + R * Math.sin(r)}px`); }
  const rr = (theta - 90) * Math.PI / 180; pts.push(`${cx + R * Math.cos(rr)}px ${cy + R * Math.sin(rr)}px`);
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{ clipPath: theta < 0.5 ? "inset(100%)" : `polygon(${pts.join(",")})` }}>{children}</AbsoluteFill>
      <div style={{ position: "absolute", left: cx, top: cy - band / 2, width: R, height: band, transformOrigin: "0 50%",
        transform: `rotate(${theta - 90}deg)`,
        background: fill(180),
        boxShadow: glow, opacity: look === "none" || p < 0.02 || p > 0.98 ? 0 : opacity }} />
    </AbsoluteFill>
  );
};
export const bandWipe = (props: BandWipeProps): TransitionPresentation<BandWipeProps> => ({ component: BandWipeComponent, props });
